"""providers -- Model-provider abstractions.

Roadmap (populated in follow-up phases):
    - src/claude_code_sdk/providers/<anthropic|bedrock|vertex|openai_compat|glm>.py
        ported from hanggent/external/claude-code/src/services/api/**
    (Anthropic Messages API, AWS Bedrock, Google Vertex AI, OpenAI-compat, GLM)

Shape reference: claude-code-sdk-ts package export `./providers`
  (see hanggent/external/claude-code-sdk-ts/package.json[exports])
"""

from __future__ import annotations

__all__: list[str] = []
