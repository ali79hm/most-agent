
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from most_agent.db.base import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    __table_args__ = (
        CheckConstraint(
            "role IN ('system', 'user', 'assistant')",
            name="ck_conversation_messages_role",
        ),
        Index(
            "ix_conversation_messages_conversation_id_id",
            "conversation_id",
            "id",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    conversation_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )
