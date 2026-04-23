"""Hook lifecycle type schemas (Pydantic v2 + Protocol).

Ported from CCB ``src/utils/hooks/hookTypes.ts`` + ``registerHook.ts``.
Shape mirrors ``claude-code-sdk-ts/src/hooks/index.ts``.

Seven lifecycle events:
    pre_tool_use, post_tool_use, user_prompt_submit,
    session_start, session_end, stop, notification.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

HookEvent = Literal[
    "pre_tool_use",
    "post_tool_use",
    "user_prompt_submit",
    "session_start",
    "session_end",
    "stop",
    "notification",
]


class HookPayload(BaseModel):
    """Payload passed to every hook handler.

    Subclasses or callers may add event-specific fields via the ``data``
    mapping; the base schema keeps the dispatch surface narrow.
    """

    model_config = ConfigDict(extra="allow")

    event: HookEvent
    session_id: str
    cwd: str
    data: dict[str, Any] = Field(default_factory=dict[str, Any])


class HookDecision(BaseModel):
    """Return value from a hook handler.

    - ``allow``: default; continue with unchanged input.
    - ``block``: short-circuit the dispatch; ``reason`` surfaces to caller.
    - ``modify``: merge ``modified`` into downstream input (last-write-wins).
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["allow", "block", "modify"] = "allow"
    reason: str | None = None
    modified: dict[str, Any] | None = None


@runtime_checkable
class HookHandler(Protocol):
    """Protocol for hook handlers: async callable with an ``event`` attribute."""

    event: HookEvent

    async def __call__(self, payload: HookPayload) -> HookDecision: ...
