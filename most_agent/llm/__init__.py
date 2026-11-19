
from most_agent.config import Settings, get_settings
from most_agent.llm.openai_compatible import OpenAICompatibleProvider
from most_agent.llm.provider import ChatMessage, LLMProvider


def create_llm_provider(
    settings: Settings | None = None,
) -> LLMProvider:
    settings = settings or get_settings()

    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleProvider(settings)

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )


__all__ = [
    "ChatMessage",
    "LLMProvider",
    "OpenAICompatibleProvider",
    "create_llm_provider",
]
