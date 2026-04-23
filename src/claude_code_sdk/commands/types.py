"""Types for slash-command registry. Ports CCB ``src/commands/**``."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class CommandContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: str
    cwd: str
    argv: str = ""
    extras: dict[str, Any] = Field(default_factory=dict[str, Any])


class CommandResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    output: str
    is_error: bool = False


@runtime_checkable
class CommandHandler(Protocol):
    async def __call__(self, ctx: CommandContext) -> CommandResult | str: ...


class Command(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str
    description: str = ""
    handler: Any  # CommandHandler; Pydantic cannot validate Protocol directly
    hidden: bool = False
