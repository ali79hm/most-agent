
import uuid

from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKeyConstraint,
    Integer,
    SmallInteger,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base
from most_agent.db.models.media import MediaItem


class SeriesDetails(Base):
    __tablename__ = "series_details"

    __table_args__ = (
        CheckConstraint(
            "media_type = 'series'",
            name="ck_series_details_media_type",
        ),

        CheckConstraint(
            "end_year IS NULL OR end_year > 0",
            name="ck_series_details_end_year_positive",
        ),

        CheckConstraint(
            "end_year IS NULL OR end_date IS NULL",
            name="ck_series_details_end_date_exclusive",
        ),

        CheckConstraint(
            "typical_episode_runtime_minutes IS NULL "
            "OR typical_episode_runtime_minutes > 0",
            name="ck_series_details_runtime_positive",
        ),

        CheckConstraint(
            "season_count IS NULL OR season_count > 0",
            name="ck_series_details_season_count_positive",
        ),

        CheckConstraint(
            "episode_count IS NULL OR episode_count > 0",
            name="ck_series_details_episode_count_positive",
        ),

        ForeignKeyConstraint(
            ["media_id", "media_type"],
            ["media_items.id", "media_items.media_type"],
            name="fk_series_details_media_type",
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
        default="series",
        server_default=text("'series'"),
    )

    end_year: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    typical_episode_runtime_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    season_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    episode_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    media: Mapped["MediaItem"] = relationship(
        back_populates="series_details",
    )

    episodes: Mapped[list["EpisodeDetails"]] = relationship(
        "EpisodeDetails",
        back_populates="series",
        cascade="all, delete-orphan",
    )
