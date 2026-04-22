"""permissions -- Tool-call permission context + policies.

Roadmap (populated in follow-up phases):
    - src/claude_code_sdk/permissions/<context|policy|prompts>.py
        ported from hanggent/external/claude-code/src/permissions/**
                    + hanggent/external/claude-code/src/ToolPermissionContext.ts

Shape reference: claude-code-sdk-ts package export `./permissions`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

__all__: list[str] = []
