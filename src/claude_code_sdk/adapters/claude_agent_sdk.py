"""Bidirectional bridge between claude_code_sdk.tools.Tool and
Anthropic's claude-agent-sdk ``SdkMcpTool``.

Install the optional extra to use the ``to_agent_sdk_tool`` direction::

    pip install "claude-code-sdk[agent-sdk]"

The ``from_agent_sdk_tool`` direction works without the extra installed --
it only needs a duck-typed object with ``name``, ``description``,
``input_schema``, and ``handler`` attributes.

Ported from claude-code-sdk-ts/src/adapters/claude-agent-sdk.ts (Phase 999.1).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, create_model

from claude_code_sdk.tools import (
    PermissionResult,
    Tool,
    ToolContext,
    ToolResult,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from claude_agent_sdk import SdkMcpTool  # type: ignore[import-not-found]


class _DictModel(BaseModel):
    """Permissive Pydantic model used when bridging from an external JSON schema."""

    model_config = ConfigDict(extra="allow")


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


def to_agent_sdk_tool(tool: Tool[Any, Any, Any]) -> SdkMcpTool:
    """Wrap a CCB-native Tool so claude-agent-sdk can register it as an MCP tool.

    Raises:
        ImportError: if the optional ``claude-agent-sdk`` extra is not installed.
    """
    try:
        from claude_agent_sdk import SdkMcpTool  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "claude-agent-sdk is not installed. "
            'Run `pip install "claude-code-sdk[agent-sdk]"` to enable adapter usage.'
        ) from e

    async def handler(args: dict[str, Any]) -> Any:
        parsed = tool.validate_input(args)
        ctx = ToolContext(session_id="adapter", cwd=".", abort_signal=None)
        result: ToolResult[Any] | None = None
        async for event in tool.call(parsed, ctx):
            if isinstance(event, ToolResult):
                result = event
        if result is None:
            raise RuntimeError(f"Tool {tool.name} did not yield a ToolResult")
        return result.output

    return SdkMcpTool(
        name=tool.name,
        description=tool.description,
        input_schema=tool.input_model.model_json_schema(),
        handler=handler,
    )


def from_agent_sdk_tool(sdk_tool: Any) -> Tool[Any, Any, Any]:
    """Wrap an Anthropic claude-agent-sdk ``SdkMcpTool`` (or duck-typed stand-in)
    so CCB-native consumers can treat it as a :class:`claude_code_sdk.tools.Tool`.

    The returned object is permissive: it accepts any input JSON dict (via
    ``ConfigDict(extra="allow")``) and delegates call-time behaviour to the
    external tool's handler.
    """
    _synthesised_model: type[BaseModel] = create_model(
        f"{sdk_tool.name}Input",
        __base__=_DictModel,
    )
    _name: str = sdk_tool.name
    _description: str = sdk_tool.description
    _handler = sdk_tool.handler

    class _AgentSdkToolAdapter:
        name: str = _name
        description: str = _description
        input_model: type[BaseModel] = _synthesised_model
        is_read_only: bool = False
        is_enabled: bool = True

        def validate_input(self, raw: dict[str, Any]) -> BaseModel:
            return _synthesised_model.model_validate(raw)

        async def check_permissions(
            self, input: BaseModel, context: ToolContext
        ) -> PermissionResult:
            return PermissionResult(decision="allow")

        async def can_use_tool(self, context: ToolContext) -> bool:
            return True

        async def call(
            self, input: BaseModel, context: ToolContext
        ) -> AsyncIterator[ToolResult[Any]]:
            args = (
                input.model_dump() if hasattr(input, "model_dump") else dict(input)  # type: ignore[arg-type]
            )
            output = await _maybe_await(_handler(args))
            yield ToolResult(output=output)

        def render_result_for_assistant(self, result: ToolResult[Any]) -> str:
            return str(result.output)

    return _AgentSdkToolAdapter()  # type: ignore[return-value]


__all__ = ["from_agent_sdk_tool", "to_agent_sdk_tool"]
