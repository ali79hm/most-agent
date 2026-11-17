
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base


class MediaItem(Base):
    __tablename__ = "media_items"

    __table_args__ = (
        UniqueConstraint("imdb_id", name="uq_media_items_imdb_id"),

        CheckConstraint(
            "media_type IN ('movie', 'series', 'episode')",
            name="ck_media_items_media_type",
        ),

        CheckConstraint(
            "release_year IS NULL OR release_year > 0",
            name="ck_media_items_release_year_positive",
        ),

        CheckConstraint(
            "release_year IS NULL OR release_date IS NULL",
            name="ck_media_items_release_date_exclusive",
        ),

        CheckConstraint(
            "imdb_rating IS NULL OR "
            "(imdb_rating >= 0 AND imdb_rating <= 10)",
            name="ck_media_items_imdb_rating_range",
        ),
    )

    # Identity
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    imdb_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Common media information
    media_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    poster: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Release information
    release_year: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # IMDb information
    imdb_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    imdb_rating: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 1),
        nullable=True,
    )

    # Lists
    genres: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    countries: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    movie_details: Mapped["MovieDetails | None"] = relationship(
        "MovieDetails",
        back_populates="media",
        uselist=False,
        cascade="all, delete-orphan",
    )

    series_details: Mapped["SeriesDetails | None"] = relationship(
        "SeriesDetails",
        back_populates="media",
        uselist=False,
        cascade="all, delete-orphan",
    )

    episode_details: Mapped["EpisodeDetails | None"] = relationship(
        "EpisodeDetails",
        back_populates="media",
        uselist=False,
        cascade="all, delete-orphan",
    )

    embeddings: Mapped[list["MediaEmbedding"]] = relationship(
        "MediaEmbedding",
        back_populates="media",
        cascade="all, delete-orphan",
    )
