"""MCP public type schemas (Pydantic v2).

Ports the typed surface of CCB's MCP client (see
``hanggent/external/claude-code/src/services/mcp*`` + CCB
``claude-code-sdk-ts/src/mcp/index.ts``) to Python with Pydantic v2 models.

Field names are snake_case; all models round-trip cleanly through
``model_dump()`` / ``model_validate()``.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

McpTransport = Literal["stdio", "sse", "http"]


class McpServerSpec(BaseModel):
    """Declarative spec for an MCP server the SDK should connect to.

    Use ``transport="stdio"`` with ``command``/``args``/``env`` for a local
    process, or ``transport="sse"`` with ``url``/``headers`` for a remote
    server. ``http`` is reserved for future PyPI ``mcp`` transports.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    transport: McpTransport = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)


class McpToolRef(BaseModel):
    """A tool discovered via :meth:`McpClient.list_tools` -- transport-normalized."""

    model_config = ConfigDict(extra="ignore")

    server: str
    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class McpCallResult(BaseModel):
    """Result of :meth:`McpClient.call_tool`; mirrors MCP ``CallToolResult``."""

    model_config = ConfigDict(extra="allow")

    is_error: bool = False
    content: list[dict[str, Any]] = Field(default_factory=list[dict[str, Any]])
