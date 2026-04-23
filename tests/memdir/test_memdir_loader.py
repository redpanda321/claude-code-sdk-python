"""Tests for claude_code_sdk.memdir.load_memories walk-up + dedupe."""

from __future__ import annotations

from pathlib import Path

from claude_code_sdk.memdir import MemoryEntry, load_memories, walk_up


def test_walk_up_yields_cwd_and_ancestors(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    ancestors = list(walk_up(deep))
    assert ancestors[0] == deep.resolve()
    assert tmp_path.resolve() in ancestors


def test_load_memories_collects_agents_and_claude_md(tmp_path: Path) -> None:
    # root/AGENTS.md + root/sub/cwd/CLAUDE.md
    root = tmp_path / "root"
    (root / "sub" / "cwd").mkdir(parents=True)
    (root / "AGENTS.md").write_text("top-agents", encoding="utf-8")
    (root / "sub" / "cwd" / "CLAUDE.md").write_text("leaf-claude", encoding="utf-8")
    entries = load_memories(root / "sub" / "cwd")
    names = {e.name for e in entries}
    assert "AGENTS" in names
    assert "CLAUDE" in names
    assert all(isinstance(e, MemoryEntry) for e in entries)
    assert all(e.scope == "project" for e in entries)


def test_load_memories_picks_up_claude_memories_subdir(tmp_path: Path) -> None:
    root = tmp_path / "root"
    memdir = root / ".claude" / "memories"
    memdir.mkdir(parents=True)
    (memdir / "alpha.md").write_text("a", encoding="utf-8")
    (memdir / "beta.md").write_text("b", encoding="utf-8")
    entries = load_memories(root)
    names = sorted(e.name for e in entries)
    assert "alpha" in names
    assert "beta" in names


def test_load_memories_extra_roots_scope_user(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    user_root = tmp_path / "home"
    user_root.mkdir()
    (user_root / "AGENTS.md").write_text("user-agents", encoding="utf-8")
    entries = load_memories(project, extra_roots=[user_root])
    user_entries = [e for e in entries if e.scope == "user"]
    assert len(user_entries) == 1
    assert user_entries[0].name == "AGENTS"
    assert user_entries[0].content == "user-agents"


def test_load_memories_dedupes_by_scope_and_name(tmp_path: Path) -> None:
    # Nested AGENTS.md at two levels; closer one should win (last write in walk_up).
    root = tmp_path / "root"
    (root / "sub").mkdir(parents=True)
    (root / "AGENTS.md").write_text("outer", encoding="utf-8")
    (root / "sub" / "AGENTS.md").write_text("inner", encoding="utf-8")
    entries = load_memories(root / "sub")
    agents = [e for e in entries if e.name == "AGENTS" and e.scope == "project"]
    assert len(agents) == 1
    # walk_up starts at cwd and walks outward; last write wins -> outer parent overrides child.
    # This matches the plan's "Later entries override earlier" contract.
    assert agents[0].content == "outer"


def test_load_memories_no_files_returns_empty(tmp_path: Path) -> None:
    entries = load_memories(tmp_path)
    assert entries == []
