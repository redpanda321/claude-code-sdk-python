from __future__ import annotations

import pytest

from claude_code_sdk.commands import (
    Command,
    CommandContext,
    CommandNotFoundError,
    CommandRegistry,
    CommandResult,
    parse_invocation,
)


async def _echo(ctx: CommandContext) -> str:
    return f"echoed:{ctx.argv}"


async def _rich(ctx: CommandContext) -> CommandResult:
    return CommandResult(output=f"rich:{ctx.argv}", is_error=False)


def test_parse_invocation_strips_slash_and_lowercases() -> None:
    assert parse_invocation("/Init foo bar") == ("init", "foo bar")


def test_parse_invocation_no_slash() -> None:
    assert parse_invocation("commit message here") == ("commit", "message here")


def test_parse_invocation_preserves_internal_spaces() -> None:
    assert parse_invocation("/init  foo  bar") == ("init", "foo  bar")


def test_register_resolve_case_insensitive() -> None:
    reg = CommandRegistry()
    reg.register(Command(name="Echo", handler=_echo))
    assert reg.resolve("ECHO").name == "Echo"
    assert reg.resolve("echo").name == "Echo"


def test_unregister_missing_raises() -> None:
    reg = CommandRegistry()
    with pytest.raises(CommandNotFoundError):
        reg.unregister("ghost")


def test_resolve_missing_raises() -> None:
    reg = CommandRegistry()
    with pytest.raises(CommandNotFoundError):
        reg.resolve("ghost")


async def test_dispatch_wraps_plain_str() -> None:
    reg = CommandRegistry()
    reg.register(Command(name="echo", handler=_echo))
    result = await reg.dispatch("/echo hello")
    assert isinstance(result, CommandResult)
    assert result.output == "echoed:hello"
    assert result.is_error is False


async def test_dispatch_passes_through_command_result() -> None:
    reg = CommandRegistry()
    reg.register(Command(name="rich", handler=_rich))
    result = await reg.dispatch("/rich args")
    assert result.output == "rich:args"


def test_list_all_excludes_hidden_by_default() -> None:
    reg = CommandRegistry()
    reg.register(Command(name="visible", handler=_echo))
    reg.register(Command(name="secret", handler=_echo, hidden=True))
    visible = reg.list_all()
    assert {c.name for c in visible} == {"visible"}
    both = reg.list_all(include_hidden=True)
    assert {c.name for c in both} == {"visible", "secret"}
