from __future__ import annotations

from claude_code_sdk.permissions import PermissionResult, ToolPermissionContext
from claude_code_sdk.tools import PermissionResult as ToolsPermissionResult


def test_permission_result_is_reexport() -> None:
    # Single source of truth: permissions.PermissionResult *is* tools.PermissionResult.
    assert PermissionResult is ToolsPermissionResult


def test_deny_beats_allow() -> None:
    ctx = ToolPermissionContext.from_strings(allow=["Bash"], deny=["Bash(rm *)"])
    result = ctx.decide("Bash", {"command": "rm -rf /"})
    assert result.decision == "deny"
    assert result.reason is not None
    assert "rm *" in result.reason


def test_allow_wins_over_ask() -> None:
    ctx = ToolPermissionContext.from_strings(allow=["Bash(git *)"], ask=["Bash"])
    result = ctx.decide("Bash", {"command": "git status"})
    assert result.decision == "allow"


def test_ask_fallback_when_no_allow_matches() -> None:
    ctx = ToolPermissionContext.from_strings(allow=["Bash(git *)"], ask=["Bash"])
    result = ctx.decide("Bash", {"command": "ls -la"})
    assert result.decision == "ask"


def test_empty_context_returns_ask_with_no_matching_rule() -> None:
    ctx = ToolPermissionContext()
    result = ctx.decide("Bash", {"command": "whatever"})
    assert result.decision == "ask"
    assert result.reason == "no matching rule"


def test_from_strings_round_trip() -> None:
    ctx = ToolPermissionContext.from_strings(
        allow=["Read", "Bash(git *)"],
        deny=["Bash(rm *)"],
        ask=["Write"],
    )
    assert len(ctx.allow) == 2
    assert len(ctx.deny) == 1
    assert len(ctx.ask) == 1
    assert ctx.allow[0].tool == "Read"
    assert ctx.allow[1].pattern == "git *"
