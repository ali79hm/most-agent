
from __future__ import annotations

import json
from collections.abc import AsyncIterator, Sequence

import httpx

from most_agent.config import Settings, get_settings
from most_agent.llm.provider import ChatMessage


class OpenAICompatibleProvider:

    def __init__(
        self,
        settings: Settings | None = None,
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

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:

        payload = self._build_payload(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        response = await self._client.post(
            self._chat_url,
            json=payload,
        )

        response.raise_for_status()

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "LLM provider returned invalid JSON"
            ) from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Unexpected LLM response format"
            ) from exc

        if not isinstance(content, str):
            raise RuntimeError(
                "LLM returned invalid message content"
            )

        return content

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:

        payload = self._build_payload(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async with self._client.stream(
            "POST",
            self._chat_url,
            json=payload,
        ) as response:

            response.raise_for_status()

            received_done = False

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
                    raise RuntimeError(
                        "LLM returned invalid streaming JSON"
                    ) from exc

                choices = chunk.get("choices")

                if not choices:
                    continue

                delta = choices[0].get("delta") or {}
                content = delta.get("content")

                if isinstance(content, str) and content:
                    yield content

            if not received_done:
                raise RuntimeError(
                    "LLM stream ended before [DONE]"
                )
