
from uuid import UUID

from sqlalchemy import func, select, update

from most_agent.db.models import (
    Conversation,
    ConversationMessage,
)
from most_agent.db.session import SessionFactory
from most_agent.llm.provider import ChatMessage, ChatRole


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
    role: ChatRole,
    content: str,
) -> int:
    """Save a message and return its database ID."""

    if role not in ("system", "user", "assistant"):
        raise ValueError(f"Invalid message role: {role}")

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
    """Load messages in their original order."""

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
