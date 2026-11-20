
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str


@dataclass(frozen=True, slots=True)
class TokenUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class CompletionMetrics:
    total_duration_seconds: float
    time_to_first_text_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    model: str | None
    finish_reason: str | None
    usage: TokenUsage | None
    metrics: CompletionMetrics


@dataclass(frozen=True, slots=True)
class ChatChunk:
    content: str = ""
    model: str | None = None
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    metrics: CompletionMetrics | None = None


class LLMProviderError(Exception):
    """Base exception for all LLM provider failures."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMTimeoutError(LLMProviderError):
    """The provider request timed out."""


class LLMConnectionError(LLMProviderError):
    """The provider could not be reached."""


class LLMAPIError(LLMProviderError):
    """The provider returned an unsuccessful HTTP status."""


class LLMResponseError(LLMProviderError):
    """The provider returned an invalid response."""


class LLMStreamError(LLMProviderError):
    """The provider returned an incomplete stream."""


class LLMProvider(Protocol):

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResult:
        ...

    def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ChatChunk]:
        ...

    async def aclose(self) -> None:
        ...
