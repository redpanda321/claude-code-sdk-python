"""Tests for claude_code_sdk.memdir type schemas."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from claude_code_sdk.memdir import MemoryEntry


def test_memory_entry_path_is_concrete_pathlib(tmp_path: Path) -> None:
    f = tmp_path / "AGENTS.md"
    f.write_text("hello", encoding="utf-8")
    entry = MemoryEntry(scope="project", path=f, name="AGENTS", content="hello")
    assert isinstance(entry.path, Path)
    # Must be concrete Path, not PurePosixPath/PureWindowsPath.
    assert type(entry.path).__mro__[0] is type(Path())  # type: ignore[comparison-overlap]


def test_memory_entry_rejects_unknown_scope() -> None:
    with pytest.raises(ValidationError):
        MemoryEntry.model_validate({"scope": "team", "path": Path("."), "name": "x", "content": ""})


def test_memory_entry_round_trip(tmp_path: Path) -> None:
    f = tmp_path / "CLAUDE.md"
    f.write_text("body", encoding="utf-8")
    entry = MemoryEntry(scope="user", path=f, name="CLAUDE", content="body")
    dumped = entry.model_dump()
    # path serializes as a Path-like; name + scope round-trip cleanly.
    assert dumped["scope"] == "user"
    assert dumped["name"] == "CLAUDE"
    assert dumped["content"] == "body"
