"""Budget-aware compaction gate.

Ported from CCB ``src/services/compact/autoCompactIfNeeded.ts``.
"""

from __future__ import annotations

from claude_code_sdk.providers import Message, Provider

from .microcompact import microcompact

__all__ = ["autocompact_if_needed", "estimate_tokens"]


def estimate_tokens(messages: list[Message]) -> int:
    """Char/4 heuristic matching CCB's cheap estimator."""
    total_chars = 0
    for m in messages:
        content = m.content
        if isinstance(content, str):
            total_chars += len(content)
        else:
            for block in content:
                if "text" in block:
                    total_chars += len(str(block["text"]))
    return total_chars // 4


async def autocompact_if_needed(
    messages: list[Message],
    token_budget: int,
    provider: Provider,
    *,
    keep_tail: int = 10,
) -> list[Message]:
    """Pass messages through; compact via ``microcompact`` if over budget."""
    if estimate_tokens(messages) <= token_budget:
        return list(messages)
    return await microcompact(messages, provider, keep_tail=keep_tail)
