"""Hook registry: register/unregister/dispatch lifecycle events.

Ported from CCB ``src/utils/hooks/registerHook.ts``. Handlers are grouped by
``HookEvent`` and dispatched concurrently via ``asyncio.gather``. Dispatch
short-circuits on the first ``block`` decision and otherwise merges all
``modify`` decisions in registration order.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from .types import HookDecision, HookEvent, HookHandler, HookPayload


class HookNotFoundError(KeyError):
    """Raised by :meth:`HookRegistry.unregister` when the handler is absent."""


class HookRegistry:
    """Typed registry of hook handlers keyed by :data:`HookEvent`."""

    def __init__(self) -> None:
        self._handlers: dict[HookEvent, list[HookHandler]] = defaultdict(list)

    def register(self, handler: HookHandler) -> None:
        self._handlers[handler.event].append(handler)

    def unregister(self, handler: HookHandler) -> None:
        bucket = self._handlers.get(handler.event)
        if bucket is None or handler not in bucket:
            raise HookNotFoundError(f"hook not registered for event {handler.event!r}")
        bucket.remove(handler)

    def list(self, event: HookEvent) -> list[HookHandler]:
        return list(self._handlers.get(event, ()))

    async def dispatch(self, payload: HookPayload) -> HookDecision:
        """Run all handlers for ``payload.event`` concurrently.

        Returns:
            - ``block`` (first encountered) if any handler blocks.
            - ``modify`` with merged patches if any handler modified (last-write-wins).
            - ``allow`` otherwise.
        """
        handlers = list(self._handlers.get(payload.event, ()))
        if not handlers:
            return HookDecision(action="allow")
        results = await asyncio.gather(
            *(h(payload) for h in handlers),
            return_exceptions=False,
        )
        merged: dict[str, Any] = {}
        for r in results:
            if r.action == "block":
                return r
            if r.action == "modify" and r.modified:
                merged.update(r.modified)
        if merged:
            return HookDecision(action="modify", modified=merged)
        return HookDecision(action="allow")
