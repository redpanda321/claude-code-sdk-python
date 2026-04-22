"""hooks -- Agent-lifecycle hook system.

Roadmap (populated in follow-up phases):
    - src/claude_code_sdk/hooks/<registry|types|runner>.py
        ported from hanggent/external/claude-code/src/hooks/**
                    + hanggent/external/claude-code/src/hookRegistry.ts

Shape reference: claude-code-sdk-ts package export `./hooks`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

__all__: list[str] = []
