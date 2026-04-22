"""compaction -- Context-window compaction strategies.

Roadmap (populated in follow-up phases):
    - src/claude_code_sdk/compaction/<snip|micro|strategy>.py
        ported from hanggent/external/claude-code/src/compaction/**
                    + hanggent/external/claude-code/src/snipCompact.ts
                    + hanggent/external/claude-code/src/microcompact.ts

Shape reference: claude-code-sdk-ts package export `./compaction`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

__all__: list[str] = []
