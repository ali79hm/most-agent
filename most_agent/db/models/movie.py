
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base
from most_agent.db.models.media import MediaItem


class MovieDetails(Base):
    __tablename__ = "movie_details"

    __table_args__ = (
        CheckConstraint(
            "runtime_minutes IS NULL OR runtime_minutes > 0",
            name="ck_movie_details_runtime_positive",
        ),
    )

    media_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("media_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    runtime_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    media: Mapped["MediaItem"] = relationship(
        back_populates="movie_details",
    )
