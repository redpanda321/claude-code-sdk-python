"""Slash-command registry + types.

Ports CCB ``src/commands/**`` per CONTEXT D-19. Built-in commands
(``/init``, ``/commit``, ``/review``, ...) are deferred to a follow-up
phase; this module exposes the typed registry contract only.
"""

from __future__ import annotations

from .registry import CommandNotFoundError, CommandRegistry, parse_invocation
from .types import Command, CommandContext, CommandHandler, CommandResult

__all__ = [
    "Command",
    "CommandContext",
    "CommandHandler",
    "CommandNotFoundError",
    "CommandRegistry",
    "CommandResult",
    "parse_invocation",
]
