
from decimal import Decimal, InvalidOperation
from typing import Literal

from sqlalchemy import Integer, cast, extract, func, select

from most_agent.config import Settings, get_settings
from most_agent.db.models import MediaEmbedding, MediaItem
from most_agent.db.session import SessionFactory
from most_agent.embeddings.client import EmbeddingClient
from most_agent.embeddings.service import EMBEDDING_TYPE


MediaType = Literal["movie", "series", "episode"]


async def search_media(
    query: str,
    *,
    top_k: int = 10,
    media_type: MediaType | None = None,
    genres: list[str] | None = None,
    countries: list[str] | None = None,
    min_release_year: int | None = None,
    max_release_year: int | None = None,
    min_imdb_rating: Decimal | None = None,
    settings: Settings | None = None,
) -> list[dict]:
    """
    Search movies, series, and episodes using semantic similarity.

    Metadata filters are applied directly in PostgreSQL.
    Results are ranked by cosine similarity.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty")

    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    if media_type not in (None, "movie", "series", "episode"):
        raise ValueError(f"Unsupported media type: {media_type}")

    if (
        min_release_year is not None
        and max_release_year is not None
        and min_release_year > max_release_year
    ):
        raise ValueError(
            "min_release_year cannot exceed max_release_year"
        )

    if min_imdb_rating is not None:
        try:
            min_imdb_rating = Decimal(str(min_imdb_rating))
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid IMDb rating") from None

        if (
            not min_imdb_rating.is_finite()
            or not Decimal("0") <= min_imdb_rating <= Decimal("10")
        ):
            raise ValueError(
                "min_imdb_rating must be between 0 and 10"
            )

    settings = settings or get_settings()

    async with EmbeddingClient(settings) as client:
        query_vector = await client.embed_query(query)

    # Prefer release_year.
    # If unavailable, extract year from release_date.
    release_year = func.coalesce(
        MediaItem.release_year,
        cast(
            extract("year", MediaItem.release_date),
            Integer,
        ),
    )

    # PostgreSQL pgvector cosine distance.
    distance = MediaEmbedding.embedding.cosine_distance(
        query_vector
    )

    similarity = (1.0 - distance).label("cosine_similarity")

    statement = (
        select(
            MediaItem.id.label("media_id"),
            MediaItem.name.label("title"),
            MediaItem.media_type,
            MediaItem.description,
            release_year.label("release_year"),
            MediaItem.genres,
            MediaItem.countries,
            MediaItem.imdb_rating,
            similarity,
        )
        .select_from(MediaEmbedding)
        .join(
            MediaItem,
            MediaItem.id == MediaEmbedding.media_id,
        )
        .where(
            MediaEmbedding.model_name == settings.embedding_model_name,
            MediaEmbedding.embedding_type == EMBEDDING_TYPE,
        )
    )

    # Apply metadata filters
    if media_type is not None:
        statement = statement.where(
            MediaItem.media_type == media_type
        )

    if genres:
        statement = statement.where(
            MediaItem.genres.overlap(genres)
        )

    if countries:
        statement = statement.where(
            MediaItem.countries.overlap(countries)
        )

    if min_release_year is not None:
        statement = statement.where(
            release_year >= min_release_year
        )

    if max_release_year is not None:
        statement = statement.where(
            release_year <= max_release_year
        )

    if min_imdb_rating is not None:
        statement = statement.where(
            MediaItem.imdb_rating >= min_imdb_rating
        )

    statement = (
        statement
        .order_by(
            distance.asc(),
            MediaItem.id.asc(),
        )
        .limit(top_k)
    )

    with SessionFactory() as session:
        results = session.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in results]
