"""Slash-command registry + invocation parser.

Ports CCB ``src/commands/**``. Built-in command bodies (``/init``,
``/commit``, ``/review``, ...) land in a follow-up phase; this module
provides only the typed registry contract.
"""

from __future__ import annotations

from .types import Command, CommandContext, CommandHandler, CommandResult


class CommandNotFoundError(KeyError):
    """Raised when an unknown command is requested."""


def parse_invocation(raw: str) -> tuple[str, str]:
    """Split ``/name rest of args`` into ``("name", "rest of args")``.

    The name is lowercased for case-insensitive lookup; the args portion
    preserves internal whitespace (only the boundary is consumed).
    """
    text = raw.strip()
    if text.startswith("/"):
        text = text[1:]
    name, _, argv = text.partition(" ")
    return name.lower(), argv.strip()


class CommandRegistry:
    """Case-insensitive registry of slash commands."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, cmd: Command) -> None:
        self._commands[cmd.name.lower()] = cmd

    def unregister(self, name: str) -> None:
        try:
            del self._commands[name.lower()]
        except KeyError as e:
            raise CommandNotFoundError(name) from e

    def resolve(self, name: str) -> Command:
        key = name.lower()
        if key not in self._commands:
            raise CommandNotFoundError(name)
        return self._commands[key]

    def list_all(self, *, include_hidden: bool = False) -> list[Command]:
        return [c for c in self._commands.values() if include_hidden or not c.hidden]

    async def dispatch(
        self,
        raw: str,
        *,
        ctx: CommandContext | None = None,
        session_id: str = "sdk",
        cwd: str = ".",
    ) -> CommandResult:
        name, argv = parse_invocation(raw)
        cmd = self.resolve(name)
        effective_ctx = ctx or CommandContext(session_id=session_id, cwd=cwd, argv=argv)
        handler: CommandHandler = cmd.handler
        raw_result = await handler(effective_ctx)
        if isinstance(raw_result, CommandResult):
            return raw_result
        return CommandResult(output=str(raw_result))
