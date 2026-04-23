from __future__ import annotations

import pytest

from claude_code_sdk.permissions import PermissionRule, match_rule, parse_rule


def test_parse_rule_without_pattern() -> None:
    rule = parse_rule("Bash")
    assert rule.tool == "Bash"
    assert rule.pattern is None


def test_parse_rule_with_glob_pattern() -> None:
    rule = parse_rule("Bash(git *)")
    assert rule.tool == "Bash"
    assert rule.pattern == "git *"


def test_parse_rule_invalid_raises() -> None:
    with pytest.raises(ValueError, match="invalid permission rule"):
        parse_rule("bad!rule")


def test_match_rule_tool_mismatch_returns_false() -> None:
    rule = PermissionRule(tool="Bash", pattern=None)
    assert match_rule(rule, "Read", {"command": "ls"}) is False


def test_match_rule_no_pattern_matches_all_inputs() -> None:
    rule = PermissionRule(tool="Bash", pattern=None)
    assert match_rule(rule, "Bash", {"command": "anything"}) is True


def test_match_rule_glob_pattern_matches_primary_field() -> None:
    rule = PermissionRule(tool="Bash", pattern="git *")
    assert match_rule(rule, "Bash", {"command": "git status"}) is True
    assert match_rule(rule, "Bash", {"command": "rm -rf /"}) is False


def test_match_rule_read_uses_path_field() -> None:
    rule = PermissionRule(tool="Read", pattern="/etc/*")
    assert match_rule(rule, "Read", {"path": "/etc/hosts"}) is True
    assert match_rule(rule, "Read", {"path": "/home/user"}) is False
