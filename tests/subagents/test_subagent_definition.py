from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from claude_code_sdk.subagents import SubagentDefinition, load_definition


def test_default_fields() -> None:
    d = SubagentDefinition(name="researcher")
    assert d.name == "researcher"
    assert d.model == "claude-sonnet-4"
    assert d.system_prompt == ""
    assert d.tools == []
    assert d.allow_list == []


def test_missing_name_raises() -> None:
    with pytest.raises(ValidationError):
        SubagentDefinition()  # type: ignore[call-arg]


def test_load_definition_from_json(tmp_path: Path) -> None:
    payload = {
        "name": "reviewer",
        "description": "Reviews code",
        "model": "claude-opus-4",
        "system_prompt": "You review code.",
        "tools": ["Read", "Grep"],
    }
    p = tmp_path / "reviewer.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    d = load_definition(p)
    assert d.name == "reviewer"
    assert d.model == "claude-opus-4"
    assert d.tools == ["Read", "Grep"]
