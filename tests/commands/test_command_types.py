from __future__ import annotations

from claude_code_sdk.commands import Command, CommandContext, CommandResult


async def _noop(ctx: CommandContext) -> str:
    return ctx.argv


def test_command_context_round_trip() -> None:
    ctx = CommandContext(session_id="s", cwd=".", argv="foo bar", extras={"k": 1})
    assert ctx.argv == "foo bar"
    assert ctx.extras == {"k": 1}


def test_command_context_allows_extras() -> None:
    # extra="allow" lets callers stash arbitrary sidecar keys
    ctx = CommandContext.model_validate({"session_id": "s", "cwd": ".", "weird": True})
    dumped = ctx.model_dump()
    assert dumped["weird"] is True


def test_command_result_is_error_defaults_false() -> None:
    r = CommandResult(output="ok")
    assert r.is_error is False


def test_command_model_round_trip() -> None:
    cmd = Command(name="echo", description="echo args", handler=_noop, hidden=False)
    assert cmd.name == "echo"
    assert cmd.description == "echo args"
    assert cmd.hidden is False
