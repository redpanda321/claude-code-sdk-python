"""mcp -- Model Context Protocol client.

Ported from CCB (see ``hanggent/external/claude-code/src/services/mcp*``).
Shape mirrors ``claude-code-sdk-ts`` package export ``./mcp``.
Transport primitive: PyPI ``mcp`` (modelcontextprotocol python-sdk).
"""

from __future__ import annotations

from .client import McpClient, mcp_client
from .types import McpCallResult, McpServerSpec, McpToolRef, McpTransport

__all__ = [
    "McpCallResult",
    "McpClient",
    "McpServerSpec",
    "McpToolRef",
    "McpTransport",
    "mcp_client",
]
