"""Subagent definition schema + JSON loader.

Ports the CCB subagent-definition shape (``src/agents/**`` + sdk-ts
``subagents/index.ts``) into a Pydantic v2 model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SubagentDefinition",
    "SubagentDispatchError",
    "SubagentEvent",
    "load_definition",
]


class SubagentDispatchError(RuntimeError):
    """Raised when a subagent cannot be registered or resolved."""


class SubagentDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str = ""
    model: str = "claude-sonnet-4"
    system_prompt: str = ""
    tools: list[str] = Field(default_factory=list[str])
    allow_list: list[str] = Field(default_factory=list[str])


class SubagentEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    kind: str  # "stream" | "tool_call" | "tool_result" | "final"
    data: dict[str, Any] = Field(default_factory=dict[str, Any])


def load_definition(path: Path) -> SubagentDefinition:
    """Load a :class:`SubagentDefinition` from a JSON file on disk."""
    text = path.read_text(encoding="utf-8")
    return SubagentDefinition.model_validate(json.loads(text))
