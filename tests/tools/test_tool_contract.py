"""Contract smoke test for claude_code_sdk.tools.Tool Protocol."""

from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from claude_code_sdk.tools import (
    PermissionResult,
    Tool,
    ToolCallProgress,
    ToolContext,
    ToolResult,
)


class EchoInput(BaseModel):
    text: str


class EchoTool:
    """Minimal Tool Protocol implementation used by the contract tests."""

    name: str = "echo"
    description: str = "Echo the input text back as output."
    input_model: type[EchoInput] = EchoInput
    is_read_only: bool = True
    is_enabled: bool = True

    def validate_input(self, raw: dict[str, Any]) -> EchoInput:
        return EchoInput.model_validate(raw)

    async def check_permissions(self, input: EchoInput, context: ToolContext) -> PermissionResult:
        return PermissionResult(decision="allow")

    async def can_use_tool(self, context: ToolContext) -> bool:
        return True

    async def call(self, input: EchoInput, context: ToolContext):
        yield ToolCallProgress(data={"step": "start"})
        yield ToolResult(output=input.text)

    def render_result_for_assistant(self, result: ToolResult[str]) -> str:
        return str(result.output)


class DenyTool(EchoTool):
    name = "deny-echo"

    async def check_permissions(self, input: EchoInput, context: ToolContext) -> PermissionResult:
        return PermissionResult(decision="deny", reason="test-denied")


def _context() -> ToolContext:
    return ToolContext(
        session_id="s1",
        cwd="/tmp",
        abort_signal=asyncio.Event(),
    )


def test_tool_is_runtime_checkable_protocol() -> None:
    """Tool must be a runtime-checkable Protocol; a conformant instance satisfies isinstance."""
    # Protocol itself is not a concrete class; check attribute presence.
    assert hasattr(Tool, "_is_protocol"), "Tool must be typing.Protocol"
    example = EchoTool()
    assert isinstance(example, Tool), "conformant tool must pass isinstance(Tool)"


def test_tool_context_is_frozen_dataclass() -> None:
    ctx = ToolContext(session_id="s1", cwd="/tmp", abort_signal=object())
    with pytest.raises(FrozenInstanceError):
        ctx.session_id = "s2"  # type: ignore[misc]


def test_permission_result_decision_values() -> None:
    assert PermissionResult(decision="allow").decision == "allow"
    assert PermissionResult(decision="deny", reason="r").reason == "r"
    assert PermissionResult(decision="ask").reason is None


@pytest.mark.asyncio
async def test_call_yields_progress_then_result() -> None:
    tool = EchoTool()
    ctx = _context()
    events: list[Any] = []
    async for ev in tool.call(tool.validate_input({"text": "hi"}), ctx):
        events.append(ev)
    assert len(events) == 2
    assert isinstance(events[0], ToolCallProgress)
    assert isinstance(events[-1], ToolResult)
    assert events[-1].output == "hi"


@pytest.mark.asyncio
async def test_check_permissions_deny_is_honoured() -> None:
    tool = DenyTool()
    ctx = _context()
    result = await tool.check_permissions(tool.validate_input({"text": "hi"}), ctx)
    assert result.decision == "deny"
    assert result.reason == "test-denied"


def test_validate_input_raises_on_bad_payload() -> None:
    tool = EchoTool()
    with pytest.raises(ValidationError):
        tool.validate_input({"wrong_field": 123})
