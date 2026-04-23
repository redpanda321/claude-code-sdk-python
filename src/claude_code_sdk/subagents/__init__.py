"""Subagent registry + dispatcher.

Ported from CCB ``src/subagents/**`` + ``src/agents/**`` per CONTEXT D-19.
"""

from __future__ import annotations

from .definition import (
    SubagentDefinition,
    SubagentDispatchError,
    SubagentEvent,
    load_definition,
)
from .dispatch import SubagentDispatcher, SubagentRunResult

__all__ = [
    "SubagentDefinition",
    "SubagentDispatchError",
    "SubagentDispatcher",
    "SubagentEvent",
    "SubagentRunResult",
    "load_definition",
]
