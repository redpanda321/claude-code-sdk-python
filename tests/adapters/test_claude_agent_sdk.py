"""Tests for claude_code_sdk.adapters.claude_agent_sdk bidirectional bridge."""

from __future__ import annotations

import asyncio
import importlib
import sys
from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import BaseModel

from claude_code_sdk.tools import (
    PermissionResult,
    Tool,
    ToolContext,
    ToolResult,
)


class EchoInput(BaseModel):
    text: str


class EchoTool:
    """CCB-native Tool Protocol implementation used as fixture."""

    name: str = "echo"
    description: str = "Echo input text."
    input_model: type[EchoInput] = EchoInput
    is_read_only: bool = True
    is_enabled: bool = True

    def validate_input(self, raw: dict[str, Any]) -> EchoInput:
        return EchoInput.model_validate(raw)

    async def check_permissions(
        self, input: EchoInput, context: ToolContext
    ) -> PermissionResult:
        return PermissionResult(decision="allow")

    async def can_use_tool(self, context: ToolContext) -> bool:
        return True

    async def call(self, input: EchoInput, context: ToolContext):
        yield ToolResult(output=input.text)

    def render_result_for_assistant(self, result: ToolResult[str]) -> str:
        return str(result.output)


@dataclass
class FakeSdkMcpTool:
    """Stand-in for claude_agent_sdk.SdkMcpTool used by the `from_` tests."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Any


def _ctx() -> ToolContext:
    return ToolContext(session_id="t", cwd="/tmp", abort_signal=asyncio.Event())


# ---------- to_agent_sdk_tool ----------

def test_to_agent_sdk_tool_preserves_name_description() -> None:
    pytest.importorskip("claude_agent_sdk")
    from claude_code_sdk.adapters import to_agent_sdk_tool

    wrapped = to_agent_sdk_tool(EchoTool())
    assert wrapped.name == "echo"
    assert wrapped.description == "Echo input text."


@pytest.mark.asyncio
async def test_to_agent_sdk_tool_handler_returns_output() -> None:
    pytest.importorskip("claude_agent_sdk")
    from claude_code_sdk.adapters import to_agent_sdk_tool

    wrapped = to_agent_sdk_tool(EchoTool())
    result = await wrapped.handler({"text": "hi"})
    assert result == "hi"


def test_to_agent_sdk_tool_raises_when_extra_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force the lazy `import claude_agent_sdk` inside to_agent_sdk_tool to fail
    # regardless of whether the extra is installed locally.
    monkeypatch.setitem(sys.modules, "claude_agent_sdk", None)
    from claude_code_sdk.adapters import to_agent_sdk_tool

    with pytest.raises(ImportError, match="claude-code-sdk\\[agent-sdk\\]"):
        to_agent_sdk_tool(EchoTool())


# ---------- from_agent_sdk_tool ----------

def test_from_agent_sdk_tool_is_runtime_tool() -> None:
    from claude_code_sdk.adapters import from_agent_sdk_tool

    async def handler(args: dict[str, Any]) -> str:
        return str(args.get("text", ""))

    sdk_tool = FakeSdkMcpTool(
        name="fake",
        description="fake tool",
        input_schema={"type": "object"},
        handler=handler,
    )
    wrapped = from_agent_sdk_tool(sdk_tool)
    assert isinstance(wrapped, Tool)
    assert wrapped.name == "fake"


@pytest.mark.asyncio
async def test_from_agent_sdk_tool_call_drains_to_result() -> None:
    from claude_code_sdk.adapters import from_agent_sdk_tool

    async def handler(args: dict[str, Any]) -> str:
        return f"echo:{args['text']}"

    sdk_tool = FakeSdkMcpTool(
        name="e", description="d", input_schema={"type": "object"}, handler=handler
    )
    wrapped = from_agent_sdk_tool(sdk_tool)
    parsed = wrapped.validate_input({"text": "hi"})
    events: list[Any] = []
    async for ev in wrapped.call(parsed, _ctx()):
        events.append(ev)
    assert len(events) == 1
    assert isinstance(events[0], ToolResult)
    assert events[0].output == "echo:hi"


def test_from_agent_sdk_tool_validate_input_is_permissive() -> None:
    from claude_code_sdk.adapters import from_agent_sdk_tool

    async def handler(args: dict[str, Any]) -> str:
        return ""

    sdk_tool = FakeSdkMcpTool(
        name="e", description="d", input_schema={"type": "object"}, handler=handler
    )
    wrapped = from_agent_sdk_tool(sdk_tool)
    # Extra keys must be accepted (ConfigDict(extra="allow")).
    parsed = wrapped.validate_input({"text": "hi", "extra": 42})
    dumped = parsed.model_dump()
    assert dumped["text"] == "hi"
    assert dumped["extra"] == 42


# ---------- round-trip ----------

@pytest.mark.asyncio
async def test_round_trip_preserves_name_description_and_output() -> None:
    pytest.importorskip("claude_agent_sdk")
    from claude_code_sdk.adapters import from_agent_sdk_tool, to_agent_sdk_tool

    wrapped_out = to_agent_sdk_tool(EchoTool())
    wrapped_back = from_agent_sdk_tool(wrapped_out)
    assert wrapped_back.name == "echo"
    assert wrapped_back.description == "Echo input text."
    parsed = wrapped_back.validate_input({"text": "hi"})
    events: list[Any] = []
    async for ev in wrapped_back.call(parsed, _ctx()):
        events.append(ev)
    assert events[-1].output == "hi"


# Silence "imported but unused" if importlib ends up not referenced above.
_ = importlib
