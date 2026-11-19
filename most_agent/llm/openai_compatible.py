
from collections.abc import Sequence

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

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 256,
    ) -> str:

        if not messages:
            raise ValueError("Messages cannot be empty")

        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

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
