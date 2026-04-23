"""Tests for claude_code_sdk.mcp.McpClient lifecycle with a fake MCP transport."""

from __future__ import annotations

from typing import Any

import pytest

from claude_code_sdk.mcp import (
    McpCallResult,
    McpClient,
    McpServerSpec,
    McpToolRef,
    mcp_client,
)


class _FakeStreamCtx:
    """Async context manager returning a (read, write) stream pair."""

    def __init__(self) -> None:
        self.entered: bool = False
        self.exited: bool = False

    async def __aenter__(self) -> tuple[str, str]:
        self.entered = True
        return ("read-stream", "write-stream")

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        self.exited = True


class _FakeTool:
    def __init__(
        self,
        name: str,
        description: str = "",
        input_schema: dict[str, Any] | None = None,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.inputSchema: dict[str, Any] = input_schema or {}


class _FakeListToolsResp:
    def __init__(self, tools: list[_FakeTool]) -> None:
        self.tools: list[_FakeTool] = tools


class _FakeContent:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data: dict[str, Any] = data

    def model_dump(self) -> dict[str, Any]:
        return dict(self._data)


class _FakeCallToolResp:
    def __init__(self, is_error: bool = False, content: list[_FakeContent] | None = None) -> None:
        self.isError: bool = is_error
        self.content: list[_FakeContent] = content or []


class _FakeSession:
    """Stand-in for mcp.ClientSession; last-instance tracked in a class attr."""

    last: _FakeSession | None = None

    def __init__(self, read: Any, write: Any) -> None:
        self.read: Any = read
        self.write: Any = write
        self.initialized: bool = False
        self.closed: bool = False
        _FakeSession.last = self

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        self.closed = True

    async def initialize(self) -> None:
        self.initialized = True

    async def list_tools(self) -> _FakeListToolsResp:
        return _FakeListToolsResp(
            [
                _FakeTool("alpha", "first", {"type": "object"}),
                _FakeTool("beta"),
            ]
        )

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> _FakeCallToolResp:
        return _FakeCallToolResp(
            is_error=False,
            content=[_FakeContent({"echo": name, "args": arguments})],
        )


class _FakeStdioParams:
    def __init__(self, command: str, args: list[str], env: dict[str, str] | None) -> None:
        self.command: str = command
        self.args: list[str] = args
        self.env: dict[str, str] | None = env


@pytest.fixture
def patched_mcp(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {
        "ctxs": [],
        "stdio_params": None,
        "sse_args": None,
    }

    def fake_stdio_client(params: Any) -> _FakeStreamCtx:
        captured["stdio_params"] = params
        ctx = _FakeStreamCtx()
        captured["ctxs"].append(ctx)
        return ctx

    def fake_sse_client(url: str, headers: dict[str, str] | None = None) -> _FakeStreamCtx:
        captured["sse_args"] = (url, headers)
        ctx = _FakeStreamCtx()
        captured["ctxs"].append(ctx)
        return ctx

    _FakeSession.last = None
    monkeypatch.setattr("mcp.ClientSession", _FakeSession)
    monkeypatch.setattr("mcp.client.stdio.stdio_client", fake_stdio_client)
    monkeypatch.setattr("mcp.client.stdio.StdioServerParameters", _FakeStdioParams)
    monkeypatch.setattr("mcp.client.sse.sse_client", fake_sse_client)
    return captured


async def test_connect_stdio_initializes_session(patched_mcp: dict[str, Any]) -> None:
    c = McpClient(McpServerSpec(name="s1", command="/bin/srv", args=["-q"], env={"K": "V"}))
    await c.connect()
    assert _FakeSession.last is not None
    assert _FakeSession.last.initialized is True
    params = patched_mcp["stdio_params"]
    assert params.command == "/bin/srv"
    assert params.args == ["-q"]
    assert params.env == {"K": "V"}
    await c.close()


async def test_list_tools_returns_refs(patched_mcp: dict[str, Any]) -> None:
    c = McpClient(McpServerSpec(name="s1", command="srv"))
    await c.connect()
    tools = await c.list_tools()
    assert [t.name for t in tools] == ["alpha", "beta"]
    assert all(isinstance(t, McpToolRef) for t in tools)
    assert tools[0].server == "s1"
    assert tools[0].input_schema == {"type": "object"}
    assert tools[1].description == ""
    await c.close()


async def test_call_tool_wraps_response(patched_mcp: dict[str, Any]) -> None:
    c = McpClient(McpServerSpec(name="s1", command="srv"))
    await c.connect()
    r = await c.call_tool("echo", {"x": 1})
    assert isinstance(r, McpCallResult)
    assert r.is_error is False
    assert r.content[0]["echo"] == "echo"
    assert r.content[0]["args"] == {"x": 1}
    await c.close()


async def test_close_is_idempotent(patched_mcp: dict[str, Any]) -> None:
    c = McpClient(McpServerSpec(name="s1", command="srv"))
    await c.connect()
    await c.close()
    # Second close should be a no-op, not raise.
    await c.close()


async def test_mcp_client_contextmanager_closes_on_exception(
    patched_mcp: dict[str, Any],
) -> None:
    spec = McpServerSpec(name="s1", command="srv")
    with pytest.raises(RuntimeError):
        async with mcp_client(spec):
            assert _FakeSession.last is not None
            raise RuntimeError("boom")
    assert _FakeSession.last is not None
    assert _FakeSession.last.closed is True


async def test_connect_sse_uses_sse_client(patched_mcp: dict[str, Any]) -> None:
    c = McpClient(
        McpServerSpec(
            name="s2",
            transport="sse",
            url="https://example.com/mcp",
            headers={"X": "1"},
        )
    )
    await c.connect()
    url, headers = patched_mcp["sse_args"]
    assert url == "https://example.com/mcp"
    assert headers == {"X": "1"}
    await c.close()


async def test_list_tools_before_connect_raises() -> None:
    c = McpClient(McpServerSpec(name="s1", command="srv"))
    with pytest.raises(RuntimeError, match="connect"):
        await c.list_tools()
