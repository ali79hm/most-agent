
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select, update

from most_agent.db.models import (
    Conversation,
    ConversationMessage,
)
from most_agent.db.session import SessionFactory
from most_agent.llm.provider import ChatMessage

ConversationRole = Literal["user", "assistant"]


def create_conversation(
    title: str | None = None,
) -> UUID:
    """Create a conversation and return its UUID."""

    with SessionFactory.begin() as session:
        conversation = Conversation(title=title)

        session.add(conversation)
        session.flush()

        conversation_id = conversation.id

    return conversation_id


def add_message(
    conversation_id: UUID,
    *,
    role: ConversationRole,
    content: str,
) -> int:
    """Save a user or assistant message."""

    if role not in ("user", "assistant"):
        raise ValueError(
            "Conversation messages must have role "
            "'user' or 'assistant'"
        )

    if not content.strip():
        raise ValueError("Message content cannot be empty")

    with SessionFactory.begin() as session:
        conversation = session.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise LookupError(
                f"Conversation not found: {conversation_id}"
            )

        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        session.add(message)
        session.flush()

        message_id = message.id

        session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=func.now())
        )

    return message_id


def get_conversation_history(
    conversation_id: UUID,
) -> list[ChatMessage]:
    """Load the stored conversation in chronological order."""

    with SessionFactory() as session:
        conversation = session.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise LookupError(
                f"Conversation not found: {conversation_id}"
            )

        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.conversation_id
                == conversation_id
            )
            .order_by(ConversationMessage.id.asc())
        )

        messages = session.scalars(statement).all()

        return [
            ChatMessage(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ]


def save_turn(
    conversation_id: UUID,
    *,
    user_content: str,
    assistant_content: str,
) -> tuple[int, int]:
    """Save one completed user/assistant exchange atomically."""

    if not user_content.strip():
        raise ValueError("User message cannot be empty")

    if not assistant_content.strip():
        raise ValueError("Assistant message cannot be empty")

    with SessionFactory.begin() as session:
        conversation = session.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise LookupError(
                f"Conversation not found: {conversation_id}"
            )

        user_message = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=user_content,
        )

        assistant_message = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content,
        )

        session.add(user_message)
        session.flush()

        session.add(assistant_message)
        session.flush()

        user_message_id = user_message.id
        assistant_message_id = assistant_message.id

        session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=func.now())
        )

    return user_message_id, assistant_message_id
