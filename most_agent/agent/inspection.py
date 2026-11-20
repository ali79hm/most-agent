
from dataclasses import dataclass
from uuid import UUID

from most_agent.agent.checkpoint import open_postgres_checkpointer
from most_agent.agent.graph import create_agent_graph
from most_agent.conversations import get_conversation_history
from most_agent.llm.provider import ChatMessage


@dataclass(frozen=True, slots=True)
class ConversationInspection:
    conversation_id: UUID

    # Authoritative stored user/assistant dialogue.
    transcript: list[ChatMessage]

    # Information about the latest graph checkpoint.
    checkpoint_exists: bool
    checkpoint_state: dict
    next_nodes: tuple[str, ...]
    checkpoint_id: str | None


async def inspect_conversation(
    conversation_id: UUID,
) -> ConversationInspection:
    """Inspect stored chat history and latest graph state.

    This function never adds conversation messages
    or invokes the LLM.
    """

    # The transcript comes from our application's tables.
    transcript = get_conversation_history(conversation_id)

    config = {
        "configurable": {
            "thread_id": str(conversation_id),
        }
    }

    # Checkpoint state comes from LangGraph's own tables.
    async with open_postgres_checkpointer() as checkpointer:
        graph = create_agent_graph(checkpointer=checkpointer)

        snapshot = await graph.aget_state(config)

    checkpoint_exists = snapshot.config is not None

    checkpoint_id = None

    if snapshot.config is not None:
        checkpoint_id = snapshot.config.get(
            "configurable", {}
        ).get("checkpoint_id")

    return ConversationInspection(
        conversation_id=conversation_id,
        transcript=transcript,
        checkpoint_exists=checkpoint_exists,
        checkpoint_state=dict(snapshot.values),
        next_nodes=tuple(snapshot.next),
        checkpoint_id=checkpoint_id,
    )
