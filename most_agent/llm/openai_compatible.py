
from __future__ import annotations

import json
from collections.abc import AsyncIterator, Sequence
from time import perf_counter

import httpx

from most_agent.config import Settings, get_settings
from most_agent.llm.provider import (
    ChatChunk,
    ChatMessage,
    ChatResult,
    CompletionMetrics,
    LLMAPIError,
    LLMConnectionError,
    LLMProviderError,
    LLMResponseError,
    LLMStreamError,
    LLMTimeoutError,
    TokenUsage,
)


class OpenAICompatibleProvider:

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = settings or get_settings()

        self._model_name = settings.llm_model_name
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens

        base_url = str(settings.llm_base_url).rstrip("/")
        self._chat_url = f"{base_url}/chat/completions"

        api_key = (
            settings.llm_api_key.get_secret_value()
            if settings.llm_api_key
            else ""
        )

        headers = {}

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            timeout=settings.http_timeout_seconds,
            headers=headers,
            transport=transport,
        )

    async def __aenter__(self) -> OpenAICompatibleProvider:
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _build_payload(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict:

        if not messages:
            raise ValueError("Messages cannot be empty")

        return {
            "model": (
                model if model is not None else self._model_name
            ),
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            "temperature": (
                temperature
                if temperature is not None
                else self._temperature
            ),
            "max_tokens": (
                max_tokens
                if max_tokens is not None
                else self._max_tokens
            ),
            "stream": stream,
        }

    @staticmethod
    def _parse_usage(data: object) -> TokenUsage | None:
        if not isinstance(data, dict):
            return None

        def read_count(key: str) -> int | None:
            value = data.get(key)

            if isinstance(value, int) and not isinstance(value, bool):
                return value

            return None

        usage = TokenUsage(
            prompt_tokens=read_count("prompt_tokens"),
            completion_tokens=read_count("completion_tokens"),
            total_tokens=read_count("total_tokens"),
        )

        if (
            usage.prompt_tokens is None
            and usage.completion_tokens is None
            and usage.total_tokens is None
        ):
            return None

        return usage

    @staticmethod
    def _parse_completion(
        data: object,
        metrics: CompletionMetrics,
    ) -> ChatResult:

        if not isinstance(data, dict):
            raise LLMResponseError(
                "LLM provider returned an invalid response"
            )

        choices = data.get("choices")

        if (
            not isinstance(choices, list)
            or not choices
            or not isinstance(choices[0], dict)
        ):
            raise LLMResponseError(
                "LLM provider returned no valid choices"
            )

        message = choices[0].get("message")

        if not isinstance(message, dict):
            raise LLMResponseError(
                "LLM provider returned an invalid message"
            )

        content = message.get("content")

        if not isinstance(content, str):
            raise LLMResponseError(
                "LLM provider returned invalid message content"
            )

        model = data.get("model")
        finish_reason = choices[0].get("finish_reason")

        return ChatResult(
            content=content,
            model=model if isinstance(model, str) else None,
            finish_reason=(
                finish_reason
                if isinstance(finish_reason, str)
                else None
            ),
            usage=OpenAICompatibleProvider._parse_usage(
                data.get("usage")
            ),
            metrics=metrics,
        )

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResult:

        payload = self._build_payload(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        started_at = perf_counter()

        try:
            response = await self._client.post(
                self._chat_url,
                json=payload,
            )

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError as exc:
                raise LLMResponseError(
                    "LLM provider returned invalid JSON"
                ) from exc

            metrics = CompletionMetrics(
                total_duration_seconds=perf_counter() - started_at,
            )

            return self._parse_completion(data, metrics)

        except LLMProviderError:
            raise

        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                "LLM provider request timed out"
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise LLMAPIError(
                f"LLM provider returned HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc

        except httpx.RequestError as exc:
            raise LLMConnectionError(
                "Could not connect to LLM provider"
            ) from exc

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ChatChunk]:

        payload = self._build_payload(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        started_at = perf_counter()
        time_to_first_text = None

        received_done = False
        response_model = None
        finish_reason = None
        usage = None

        try:
            async with self._client.stream(
                "POST",
                self._chat_url,
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line.startswith("data:"):
                        continue

                    data = line[5:].strip()

                    if not data:
                        continue

                    if data == "[DONE]":
                        received_done = True
                        break

                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError as exc:
                        raise LLMResponseError(
                            "LLM provider returned invalid streaming JSON"
                        ) from exc

                    if not isinstance(chunk, dict):
                        raise LLMResponseError(
                            "Invalid streaming response structure"
                        )

                    model = chunk.get("model")

                    if isinstance(model, str):
                        response_model = model

                    chunk_usage = self._parse_usage(
                        chunk.get("usage")
                    )

                    if chunk_usage is not None:
                        usage = chunk_usage

                    choices = chunk.get("choices")

                    if choices is None and "usage" not in chunk:
                        raise LLMResponseError(
                            "Streaming response has no choices"
                        )

                    if choices is None:
                        continue

                    if not isinstance(choices, list):
                        raise LLMResponseError(
                            "Invalid streaming choices"
                        )

                    if not choices:
                        continue

                    choice = choices[0]

                    if not isinstance(choice, dict):
                        raise LLMResponseError(
                            "Invalid streaming choice"
                        )

                    reason = choice.get("finish_reason")

                    if isinstance(reason, str):
                        finish_reason = reason

                    delta = choice.get("delta") or {}

                    if not isinstance(delta, dict):
                        raise LLMResponseError(
                            "Invalid streaming delta"
                        )

                    content = delta.get("content")

                    if content is None:
                        continue

                    if not isinstance(content, str):
                        raise LLMResponseError(
                            "Invalid streaming content"
                        )

                    if content:
                        if time_to_first_text is None:
                            time_to_first_text = (
                                perf_counter() - started_at
                            )

                        yield ChatChunk(content=content)

            if not received_done:
                raise LLMStreamError(
                    "LLM stream ended before [DONE]"
                )

            metrics = CompletionMetrics(
                total_duration_seconds=perf_counter() - started_at,
                time_to_first_text_seconds=time_to_first_text,
            )

            # Final metadata-only chunk.
            yield ChatChunk(
                model=response_model,
                finish_reason=finish_reason,
                usage=usage,
                metrics=metrics,
            )

        except LLMProviderError:
            raise

        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                "LLM streaming request timed out"
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise LLMAPIError(
                f"LLM provider returned HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc

        except httpx.RequestError as exc:
            raise LLMConnectionError(
                "Connection to LLM provider failed during streaming"
            ) from exc
