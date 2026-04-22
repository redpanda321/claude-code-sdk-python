"""tools -- Public tool API (Protocol, schemas, built-in tool registry).

Roadmap (populated in follow-up plans and phases):
    - src/claude_code_sdk/tools/tool.py  (Plan 03 of this phase -- landed)
        ported from hanggent/external/claude-code/src/Tool.ts
    - src/claude_code_sdk/tools/<bash|file_read|file_edit|grep|glob|...>.py  (future)
        ported from hanggent/external/claude-code/src/tools/**

Shape reference: claude-code-sdk-ts package export `./tools`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

from .tool import (
    PermissionResult,
    Tool,
    ToolCallProgress,
    ToolContext,
    ToolResult,
)

__all__ = [
    "PermissionResult",
    "Tool",
    "ToolCallProgress",
    "ToolContext",
    "ToolResult",
]
