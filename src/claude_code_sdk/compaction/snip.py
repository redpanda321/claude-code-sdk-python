"""Non-LLM truncation. Ported from CCB ``src/services/compact/snipCompact.ts``."""

from __future__ import annotations

from claude_code_sdk.providers import Message

__all__ = ["snip_compact"]


def snip_compact(messages: list[Message], max_messages: int = 20) -> list[Message]:
    """Keep leading system messages + last ``max_messages`` non-system entries."""
    if len(messages) <= max_messages:
        return list(messages)
    system = [m for m in messages if m.role == "system"]
    non_system = [m for m in messages if m.role != "system"]
    tail = non_system[-max_messages:]
    return [*system, *tail]
