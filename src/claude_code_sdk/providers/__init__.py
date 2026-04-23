"""Provider layer. Ported 1:1 from CCB ``src/services/api/**`` per CONTEXT D-18.

All five vendors (Anthropic, Bedrock, Vertex, OpenAI-compat, GLM) implement
the :class:`Provider` Protocol. boto3 / google-auth are declared as optional
extras (``claude-code-sdk[bedrock]``, ``claude-code-sdk[vertex]``) and are
imported lazily inside their respective provider classes.
"""

from __future__ import annotations

from .anthropic import AnthropicProvider
from .base import (
    CompletionRequest,
    Message,
    Provider,
    ProviderError,
    StreamEvent,
)
from .bedrock import BedrockProvider
from .glm import GlmProvider
from .openai_compat import OpenAICompatProvider
from .vertex import VertexProvider

__all__ = [
    "AnthropicProvider",
    "BedrockProvider",
    "CompletionRequest",
    "GlmProvider",
    "Message",
    "OpenAICompatProvider",
    "Provider",
    "ProviderError",
    "StreamEvent",
    "VertexProvider",
]
