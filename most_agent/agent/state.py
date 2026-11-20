
from typing import NotRequired, TypedDict

from most_agent.llm.provider import ChatRole


class ModelMessage(TypedDict):
    role: ChatRole
    content: str


class AgentState(TypedDict):
    conversation_id: str
    user_input: str

    model_messages: NotRequired[list[ModelMessage]]
    answer: NotRequired[str]

    token_usage: NotRequired[dict[str, int | None] | None]
    latency_seconds: NotRequired[float]
