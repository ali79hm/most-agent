
from uuid import UUID

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from most_agent.agent.state import AgentState, ModelMessage
from most_agent.config import get_settings
from most_agent.conversations import (
    get_conversation_history,
    trim_messages,
)
from most_agent.llm import (
    ChatMessage,
    create_llm_provider,
)

SYSTEM_PROMPT = (
    "You are MOST-Agent, a helpful assistant for a "
    "personal movie and TV series library. "
    "Answer clearly and concisely. "
    "Do not invent facts about the user's library."
)


def prepare_context(state: AgentState) -> dict:
    """Prepare the messages for one LLM invocation."""

    settings = get_settings()

    conversation_id = UUID(state["conversation_id"])
    user_input = state["user_input"]

    if not user_input.strip():
        raise ValueError("User input cannot be empty")

    # PostgreSQL holds user/assistant dialogue only.
    history = get_conversation_history(conversation_id)

    # Add exactly one application-owned system prompt.
    # The current user input has not been saved yet.
    messages = [
        ChatMessage(
            role="system",
            content=SYSTEM_PROMPT,
        ),
        *history,
        ChatMessage(
            role="user",
            content=user_input,
        ),
    ]

    # Trim only the copy being sent to the LLM.
    trimmed = trim_messages(
        messages,
        context_window_tokens=settings.llm_context_window_tokens,
        max_output_tokens=settings.llm_max_tokens,
        safety_margin_tokens=(
            settings.llm_context_safety_margin_tokens
        ),
    )

    model_messages: list[ModelMessage] = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in trimmed
    ]

    return {
        "model_messages": model_messages,
    }


async def generate_response(state: AgentState) -> dict:
    """Generate an answer using the prepared messages."""

    messages = [
        ChatMessage(
            role=message["role"],
            content=message["content"],
        )
        for message in state["model_messages"]
    ]

    provider = create_llm_provider()

    try:
        result = await provider.complete(messages)
    finally:
        await provider.aclose()

    usage = None

    if result.usage is not None:
        usage = {
            "prompt_tokens": result.usage.prompt_tokens,
            "completion_tokens": result.usage.completion_tokens,
            "total_tokens": result.usage.total_tokens,
        }

    return {
        "answer": result.content,
        "token_usage": usage,
        "latency_seconds": (
            result.metrics.total_duration_seconds
        ),
    }



def create_agent_graph(
    *,
    checkpointer: BaseCheckpointSaver | None = None,
):
    """Build the MOST-Agent workflow with optional persistence."""

    builder = StateGraph(AgentState)

    builder.add_node("prepare_context", prepare_context)
    builder.add_node("generate_response", generate_response)

    builder.add_edge(START, "prepare_context")
    builder.add_edge("prepare_context", "generate_response")
    builder.add_edge("generate_response", END)

    return builder.compile(checkpointer=checkpointer)


# Retain the original graph for experiments without persistence.
graph = create_agent_graph()

