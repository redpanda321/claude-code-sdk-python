"""Permission context + decision surface.

Ports CCB ``src/permissions/**`` + ``src/ToolPermissionContext.ts`` per
CONTEXT D-19. :class:`PermissionResult` is re-exported from
:mod:`claude_code_sdk.tools` -- single source of truth.
"""

from __future__ import annotations

from .context import ToolPermissionContext
from .decision import PermissionResult, PermissionRule, match_rule, parse_rule

__all__ = [
    "PermissionResult",
    "PermissionRule",
    "ToolPermissionContext",
    "match_rule",
    "parse_rule",
]
