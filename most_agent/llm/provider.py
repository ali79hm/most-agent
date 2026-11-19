
from dataclasses import dataclass
from typing import Literal, Protocol, Sequence


ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str


class LLMProvider(Protocol):

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 256,
    ) -> str:
        ...

    async def aclose(self) -> None:
        ...
