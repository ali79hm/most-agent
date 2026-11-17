
import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base
from most_agent.db.models.media import MediaItem


class MovieDetails(Base):
    __tablename__ = "movie_details"

    __table_args__ = (
        CheckConstraint(
            "media_type = 'movie'",
            name="ck_movie_details_media_type",
        ),

        CheckConstraint(
            "runtime_minutes IS NULL OR runtime_minutes > 0",
            name="ck_movie_details_runtime_positive",
        ),

        ForeignKeyConstraint(
            ["media_id", "media_type"],
            ["media_items.id", "media_items.media_type"],
            name="fk_movie_details_media_type",
            ondelete="CASCADE",
        ),
    )

    media_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    media_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="movie",
        server_default=text("'movie'"),
    )

    runtime_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    media: Mapped["MediaItem"] = relationship(
        back_populates="movie_details",
    )
