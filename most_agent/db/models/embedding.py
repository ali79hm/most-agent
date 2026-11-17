
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base
from most_agent.db.models.media import MediaItem


class MediaEmbedding(Base):
    __tablename__ = "media_embeddings"

    __table_args__ = (
        UniqueConstraint(
            "media_id",
            "model_name",
            "embedding_type",
            name="uq_media_embeddings_media_model_type",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    media_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(768),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    media: Mapped["MediaItem"] = relationship(
        back_populates="embeddings",
    )
