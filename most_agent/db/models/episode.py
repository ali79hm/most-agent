
import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base
from most_agent.db.models.media import MediaItem
from most_agent.db.models.series import SeriesDetails


class EpisodeDetails(Base):
    __tablename__ = "episode_details"

    __table_args__ = (
        CheckConstraint(
            "season_number IS NULL OR season_number >= 0",
            name="ck_episode_details_season_number",
        ),

        CheckConstraint(
            "episode_number IS NULL OR episode_number > 0",
            name="ck_episode_details_episode_number",
        ),
    )

    media_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("media_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    series_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("series_details.media_id", ondelete="CASCADE"),
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
        back_populates="episodes",
    )
