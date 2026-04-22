"""adapters -- Bidirectional bridges to other agent SDKs.

Roadmap (populated in follow-up plans and phases):
    - src/claude_code_sdk/adapters/claude_agent_sdk.py  (Plan 04 of this phase)
        New module (no CCB source) -- bridges @anthropic-ai/claude-agent-sdk's
        Python binding (`claude-agent-sdk` on PyPI) to claude_code_sdk's Tool
        Protocol. Ported in spirit from Phase 999.1's TS adapter (commit 102f7b7).

Shape reference: claude-code-sdk-ts package export `./adapters/claude-agent-sdk`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

__all__: list[str] = []
