"""LLM-backed conversation summariser.

Ported from CCB ``src/services/compact/microcompact.ts``.
"""

from __future__ import annotations

from typing import Any, cast

from claude_code_sdk.providers import CompletionRequest, Message, Provider

__all__ = ["microcompact"]

_SUMMARY_SYSTEM = (
    "You are a summarizer. Produce a concise running summary of the conversation "
    "preserving tool calls, file paths, and user intent. Output plain text only."
)


async def microcompact(
    messages: list[Message],
    provider: Provider,
    *,
    keep_tail: int = 10,
    model: str = "claude-sonnet-4",
) -> list[Message]:
    """Summarise the oldest messages via ``provider``.

    Returns ``[*leading_system_messages, summary_msg, *tail]`` when compaction
    runs, else a shallow copy of the input.
    """
    if len(messages) <= keep_tail:
        return list(messages)

    head = messages[:-keep_tail]
    tail = messages[-keep_tail:]

    transcript_lines: list[str] = []
    for m in head:
        if isinstance(m.content, str):
            transcript_lines.append(f"{m.role}: {m.content}")
    transcript = "\n".join(transcript_lines)

    req = CompletionRequest(
        model=model,
        messages=[
            Message(role="system", content=_SUMMARY_SYSTEM),
            Message(role="user", content=transcript),
        ],
    )
    chunks: list[str] = []
    async for ev in provider.messages_stream(req):
        if ev.event == "content_block_delta":
            delta = cast("dict[str, Any]", ev.data.get("delta") or {})
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                if isinstance(text, str):
                    chunks.append(text)

    summary = "".join(chunks) or "(summary unavailable)"
    summary_msg = Message(
        role="system",
        content=f"Conversation summary so far:\n{summary}",
    )
    leading_system = [m for m in head if m.role == "system"]
    return [*leading_system, summary_msg, *tail]
