"""adapters -- Bidirectional bridges to other agent SDKs.

Currently populated:
    - claude_agent_sdk: bridges Anthropic's ``claude-agent-sdk`` (PyPI) to
      claude_code_sdk's Tool Protocol (Plan 04 of Phase 999.2).

Shape reference: claude-code-sdk-ts package export `./adapters/claude-agent-sdk`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

from .claude_agent_sdk import from_agent_sdk_tool, to_agent_sdk_tool

__all__ = ["from_agent_sdk_tool", "to_agent_sdk_tool"]
