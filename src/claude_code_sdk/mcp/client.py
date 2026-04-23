"""Async MCP client wrapping the PyPI ``mcp`` package transport.

Ported from CCB's MCP client surface (see
``hanggent/external/claude-code/src/services/mcp*`` + CCB
``claude-code-sdk-ts/src/mcp``). Uses lazy imports of the upstream ``mcp``
package so that importing ``claude_code_sdk.mcp`` does not pay the MCP cost
until a connection is attempted.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from .types import McpCallResult, McpServerSpec, McpToolRef


class McpClient:
    """Thin async wrapper over ``mcp.ClientSession`` keyed by server name.

    Lifecycle::

        client = McpClient(spec)
        await client.connect()
        tools = await client.list_tools()
        result = await client.call_tool("name", {...})
        await client.close()

    Prefer :func:`mcp_client` for scoped usage that closes on exit.
    """

    def __init__(self, spec: McpServerSpec) -> None:
        self.spec: McpServerSpec = spec
        self._session: Any | None = None
        self._ctx: Any | None = None

    async def connect(self) -> None:
        from mcp import ClientSession  # type: ignore[import-not-found]

        if self.spec.transport == "stdio":
            from mcp.client.stdio import (  # type: ignore[import-not-found]
                StdioServerParameters,
                stdio_client,
            )

            params = StdioServerParameters(
                command=self.spec.command or "",
                args=list(self.spec.args),
                env=dict(self.spec.env) or None,
            )
            self._ctx = stdio_client(params)
        elif self.spec.transport == "sse":
            from mcp.client.sse import sse_client  # type: ignore[import-not-found]

            self._ctx = sse_client(
                self.spec.url or "",
                headers=self.spec.headers or None,
            )
        else:
            raise NotImplementedError(f"MCP transport not supported: {self.spec.transport}")

        read, write = await self._ctx.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()

    async def list_tools(self) -> list[McpToolRef]:
        if self._session is None:
            raise RuntimeError("McpClient.connect() must be called before list_tools()")
        resp: Any = await self._session.list_tools()
        out: list[McpToolRef] = []
        for t in resp.tools:
            out.append(
                McpToolRef(
                    server=self.spec.name,
                    name=t.name,
                    description=getattr(t, "description", "") or "",
                    input_schema=getattr(t, "inputSchema", None) or {},
                )
            )
        return out

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> McpCallResult:
        if self._session is None:
            raise RuntimeError("McpClient.connect() must be called before call_tool()")
        resp: Any = await self._session.call_tool(name, arguments=arguments)
        content: list[dict[str, Any]] = []
        for c in resp.content:
            if hasattr(c, "model_dump"):
                content.append(c.model_dump())
            else:
                content.append(dict(c))
        return McpCallResult(
            is_error=bool(getattr(resp, "isError", False)),
            content=content,
        )

    async def close(self) -> None:
        if self._session is not None:
            await self._session.__aexit__(None, None, None)
            self._session = None
        if self._ctx is not None:
            await self._ctx.__aexit__(None, None, None)
            self._ctx = None


@asynccontextmanager
async def mcp_client(spec: McpServerSpec) -> AsyncIterator[McpClient]:
    """Scoped MCP client: connect on enter, close on exit (even if body raises)."""
    c = McpClient(spec)
    await c.connect()
    try:
        yield c
    finally:
        await c.close()
