
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from most_agent.config import Settings, get_settings
from most_agent.db.models import (
    EpisodeDetails,
    MediaEmbedding,
    MediaItem,
    SeriesDetails,
)
from most_agent.db.session import SessionFactory
from most_agent.embeddings.client import (
    EMBEDDING_DIMENSIONS,
    EmbeddingClient,
)
from most_agent.embeddings.hashing import build_content_hash
from most_agent.embeddings.text import build_search_text


DOCUMENT_PROMPT_NAME = "document"
EMBEDDING_TYPE = "document"


@dataclass(frozen=True)
class PendingDocument:
    media_id: UUID
    text: str
    content_hash: str
    is_update: bool


@dataclass(frozen=True)
class EmbeddingReport:
    total_media: int
    inserted: int
    updated: int
    skipped: int


async def generate_media_embeddings(
    settings: Settings | None = None,
) -> EmbeddingReport:
    """Generate and persist missing or outdated media embeddings."""

    settings = settings or get_settings()
    model_name = settings.embedding_model_name

    # ---------------------------------------
    # 1. Load media and existing hashes
    # ---------------------------------------

    with SessionFactory() as session:
        media_items = session.scalars(
            select(MediaItem)
            .options(
                selectinload(MediaItem.movie_details),
                selectinload(MediaItem.series_details),
                selectinload(MediaItem.episode_details)
                .selectinload(EpisodeDetails.series)
                .selectinload(SeriesDetails.media),
            )
            .order_by(MediaItem.name)
        ).all()

        total_media = len(media_items)

        if not media_items:
            return EmbeddingReport(0, 0, 0, 0)

        media_ids = [item.id for item in media_items]

        existing_rows = session.execute(
            select(
                MediaEmbedding.media_id,
                MediaEmbedding.content_hash,
            ).where(
                MediaEmbedding.media_id.in_(media_ids),
                MediaEmbedding.model_name == model_name,
                MediaEmbedding.embedding_type == EMBEDDING_TYPE,
            )
        ).all()

        existing_hashes = {
            media_id: content_hash
            for media_id, content_hash in existing_rows
        }

        # ---------------------------------------
        # 2. Build text and identify changes
        # ---------------------------------------

        pending = []
        skipped = 0

        for media in media_items:
            document = build_search_text(media)

            content_hash = build_content_hash(
                document,
                model_name=model_name,
                prompt_name=DOCUMENT_PROMPT_NAME,
                normalize=True,
                truncate=False,
                dimensions=EMBEDDING_DIMENSIONS,
            )

            old_hash = existing_hashes.get(media.id)

            if old_hash == content_hash:
                skipped += 1
                continue

            pending.append(
                PendingDocument(
                    media_id=media.id,
                    text=document,
                    content_hash=content_hash,
                    is_update=media.id in existing_hashes,
                )
            )

    # The database read session is now closed.

    if not pending:
        return EmbeddingReport(
            total_media=total_media,
            inserted=0,
            updated=0,
            skipped=skipped,
        )

    # ---------------------------------------
    # 3. Generate embeddings through TEI
    # ---------------------------------------

    async with EmbeddingClient(settings) as client:
        vectors = await client.embed_documents(
            [item.text for item in pending]
        )

    if len(vectors) != len(pending):
        raise RuntimeError(
            "Embedding count does not match pending document count"
        )

    # ---------------------------------------
    # 4. Prepare database records
    # ---------------------------------------

    embedding_rows = [
        {
            "media_id": item.media_id,
            "embedding": vector,
            "model_name": model_name,
            "embedding_type": EMBEDDING_TYPE,
            "content_hash": item.content_hash,
        }
        for item, vector in zip(pending, vectors, strict=True)
    ]

    # ---------------------------------------
    # 5. Insert or update embeddings
    # ---------------------------------------

    statement = pg_insert(MediaEmbedding).values(embedding_rows)

    upsert_statement = statement.on_conflict_do_update(
        constraint="uq_media_embeddings_media_model_type",
        set_={
            "embedding": statement.excluded.embedding,
            "content_hash": statement.excluded.content_hash,
        },
    )

    with SessionFactory.begin() as session:
        session.execute(upsert_statement)

    # ---------------------------------------
    # 6. Return report
    # ---------------------------------------

    inserted = sum(not item.is_update for item in pending)
    updated = sum(item.is_update for item in pending)

    return EmbeddingReport(
        total_media=total_media,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
    )
