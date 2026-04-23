"""hooks -- Agent-lifecycle hook system.

Ported from CCB ``src/utils/hooks/**`` (NOT CCB's ``src/hooks/`` which holds
React/Ink UI hooks). Shape mirrors ``claude-code-sdk-ts/src/hooks/index.ts``.

Exports:
    HookRegistry, HookNotFoundError -- registration + dispatch
    HookEvent, HookPayload, HookDecision, HookHandler -- typed contracts
"""

from __future__ import annotations

from .registry import HookNotFoundError, HookRegistry
from .types import HookDecision, HookEvent, HookHandler, HookPayload

__all__ = [
    "HookDecision",
    "HookEvent",
    "HookHandler",
    "HookNotFoundError",
    "HookPayload",
    "HookRegistry",
]
