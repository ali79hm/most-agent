
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


class EpisodeDetails(Base):
    __tablename__ = "episode_details"

    __table_args__ = (
        CheckConstraint(
            "media_type = 'episode'",
            name="ck_episode_details_media_type",
        ),

        CheckConstraint(
            "season_number IS NULL OR season_number >= 0",
            name="ck_episode_details_season_number",
        ),

        CheckConstraint(
            "episode_number IS NULL OR episode_number > 0",
            name="ck_episode_details_episode_number",
        ),

        ForeignKeyConstraint(
            ["media_id", "media_type"],
            ["media_items.id", "media_items.media_type"],
            name="fk_episode_details_media_type",
            ondelete="CASCADE",
        ),

        ForeignKeyConstraint(
            ["series_id"],
            ["series_details.media_id"],
            name="fk_episode_details_series",
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
        default="episode",
        server_default=text("'episode'"),
    )

    series_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    season_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    episode_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    media: Mapped["MediaItem"] = relationship(
        back_populates="episode_details",
    )

    series: Mapped["SeriesDetails"] = relationship(
        "SeriesDetails",
        back_populates="episodes",
    )
