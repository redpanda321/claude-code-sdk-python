"""Tool Protocol + supporting types.

Python port of hanggent/external/claude-code/src/Tool.ts .
Type-param names match the TS sibling: Input, Output, Progress.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

Input = TypeVar("Input", bound=BaseModel)
Output = TypeVar("Output")
Progress = TypeVar("Progress")


@dataclass(slots=True, frozen=True)
class ToolContext:
    """Per-call context passed to a Tool (session id, cwd, abort signal, etc.)."""

    session_id: str
    cwd: str
    abort_signal: Any  # asyncio.Event | anyio.Event -- kept Any to avoid committing
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ToolResult(Generic[Output]):
    """Return value of Tool.call() -- the assistant-visible output plus metadata."""

    output: Output
    is_error: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PermissionResult:
    """Return value of Tool.check_permissions()."""

    decision: Literal["allow", "deny", "ask"]
    reason: str | None = None


@dataclass(slots=True, frozen=True)
class ToolCallProgress(Generic[Progress]):
    """Yielded by Tool.call() while streaming (Progress is tool-specific)."""

    data: Progress


@runtime_checkable
class Tool(Protocol, Generic[Input, Output, Progress]):
    """Public tool contract. Ported from CCB ``src/Tool.ts``.

    Minimum implementation: ``name``, ``description``, ``input_model``, ``call``.
    Optional overrides: ``check_permissions``, ``can_use_tool``,
    ``validate_input``, ``render_result_for_assistant``, ``is_read_only``,
    ``is_enabled``.
    """

    name: str
    description: str
    input_model: type[Input]
    is_read_only: bool
    is_enabled: bool

    def validate_input(self, raw: Mapping[str, Any]) -> Input: ...

    async def check_permissions(self, input: Input, context: ToolContext) -> PermissionResult: ...

    async def can_use_tool(self, context: ToolContext) -> bool: ...

    def call(
        self, input: Input, context: ToolContext
    ) -> AsyncIterator[ToolCallProgress[Progress] | ToolResult[Output]]: ...

    def render_result_for_assistant(self, result: ToolResult[Output]) -> str: ...
