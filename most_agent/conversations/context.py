
from collections.abc import Sequence

from most_agent.llm.provider import ChatMessage


# Conservative overhead for role labels and chat formatting.
MESSAGE_OVERHEAD = 32

TRUNCATION_NOTICE = (
    "Earlier conversation messages were omitted due to "
    "the context limit. Do not assume their contents. "
    "Ask for clarification if needed."
)


def estimate_message_tokens(message: ChatMessage) -> int:
    """Estimate token cost conservatively using UTF-8 bytes."""

    return (
        len(message.content.encode("utf-8"))
        + len(message.role.encode("utf-8"))
        + MESSAGE_OVERHEAD
    )


def estimate_messages_tokens(
    messages: Sequence[ChatMessage],
) -> int:
    """Estimate the total cost of a collection of messages."""

    return sum(estimate_message_tokens(msg) for msg in messages)


def trim_messages(
    messages: Sequence[ChatMessage],
    *,
    context_window_tokens: int,
    max_output_tokens: int,
    safety_margin_tokens: int = 128,
) -> list[ChatMessage]:
    """Trim older messages while preserving essential context.

    System messages must appear before conversation messages.
    A truncation notice is placed in the leading system prompt.
    Original messages are never modified.
    """

    if context_window_tokens <= 0:
        raise ValueError("Context window must be positive")

    if max_output_tokens <= 0:
        raise ValueError("Maximum output tokens must be positive")

    if safety_margin_tokens < 0:
        raise ValueError("Safety margin cannot be negative")

    if not messages:
        raise ValueError("Messages cannot be empty")

    input_budget = (
        context_window_tokens
        - max_output_tokens
        - safety_margin_tokens
    )

    if input_budget <= 0:
        raise ValueError(
            "No input budget remains after output and safety reserves"
        )

    # System messages must come before user/assistant messages.
    seen_non_system = False

    for message in messages:
        if message.role == "system":
            if seen_non_system:
                raise ValueError(
                    "System messages must appear before "
                    "conversation messages"
                )
        else:
            seen_non_system = True

    # Nothing to trim.
    if estimate_messages_tokens(messages) <= input_budget:
        return list(messages)

    system_indices = {
        index
        for index, message in enumerate(messages)
        if message.role == "system"
    }

    non_system_indices = [
        index
        for index, message in enumerate(messages)
        if message.role != "system"
    ]

    required_indices = set(system_indices)

    # Always preserve the most recent conversation message.
    if non_system_indices:
        required_indices.add(non_system_indices[-1])

    # Prepare the notice at the beginning, never in the middle.
    if system_indices:
        first_system = messages[0]

        updated_system = ChatMessage(
            role="system",
            content=(
                first_system.content
                + "\n\n"
                + TRUNCATION_NOTICE
            ),
        )

        # Only the added text consumes extra space.
        notice_cost = (
            estimate_message_tokens(updated_system)
            - estimate_message_tokens(first_system)
        )
    else:
        updated_system = ChatMessage(
            role="system",
            content=TRUNCATION_NOTICE,
        )

        notice_cost = estimate_message_tokens(updated_system)

    # Reserve space for the notice before selecting history.
    history_budget = input_budget - notice_cost

    required_cost = sum(
        estimate_message_tokens(messages[index])
        for index in required_indices
    )

    if required_cost > history_budget:
        raise ValueError(
            "Required messages and truncation notice "
            "exceed the input budget"
        )

    selected_indices = set(required_indices)
    remaining_budget = history_budget - required_cost

    # Keep as many recent messages as possible.
    # Stop at the first older message that cannot fit.
    for index in reversed(non_system_indices[:-1]):
        cost = estimate_message_tokens(messages[index])

        if cost > remaining_budget:
            break

        selected_indices.add(index)
        remaining_budget -= cost

    trimmed = [
        message
        for index, message in enumerate(messages)
        if index in selected_indices
    ]

    if system_indices:
        # Replace the first system message with an extended one.
        trimmed[0] = updated_system
    else:
        # No original system message: insert one at position 0.
        trimmed.insert(0, updated_system)

    return trimmed
