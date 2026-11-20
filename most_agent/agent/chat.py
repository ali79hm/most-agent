
from dataclasses import dataclass
from uuid import UUID

from most_agent.agent.checkpoint import open_postgres_checkpointer
from most_agent.agent.graph import create_agent_graph
from most_agent.conversations import save_turn


@dataclass(frozen=True, slots=True)
class ChatTurnResult:
    conversation_id: UUID
    answer: str
    token_usage: dict[str, int | None] | None
    latency_seconds: float


async def ask_conversation(
    conversation_id: UUID,
    user_input: str,
) -> ChatTurnResult:
    """Run one chat turn and persist the completed exchange."""

    if not user_input.strip():
        raise ValueError("User input cannot be empty")

    thread_id = str(conversation_id)

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # The checkpointer persists the graph's execution state.
    async with open_postgres_checkpointer() as checkpointer:
        graph = create_agent_graph(
            checkpointer=checkpointer,
        )

        result = await graph.ainvoke(
            {
                "conversation_id": thread_id,
                "user_input": user_input,
            },
            config=config,
        )

    answer = result["answer"]

    # PostgreSQL conversation tables store the actual dialogue.
    # Both messages commit together, after successful inference.
    save_turn(
        conversation_id,
        user_content=user_input,
        assistant_content=answer,
    )

    return ChatTurnResult(
        conversation_id=conversation_id,
        answer=answer,
        token_usage=result["token_usage"],
        latency_seconds=result["latency_seconds"],
    )
