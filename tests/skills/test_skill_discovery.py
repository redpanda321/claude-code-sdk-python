from __future__ import annotations

from pathlib import Path

from claude_code_sdk.skills import discover_skills

_TEMPLATE = "---\nname: {name}\ndescription: {desc}\n---\n{body}\n"


def _write_skill(root: Path, dirname: str, *, name: str, desc: str = "", body: str = "x") -> Path:
    d = root / dirname
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(_TEMPLATE.format(name=name, desc=desc, body=body), encoding="utf-8")
    return p


def test_discover_skills_walks_multiple_roots(tmp_path: Path) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    _write_skill(root_a, "alpha", name="alpha")
    _write_skill(root_b, "beta", name="beta")
    skills = discover_skills([root_a, root_b])
    names = {s.name for s in skills}
    assert names == {"alpha", "beta"}


def test_discover_skills_later_root_overrides_by_name(tmp_path: Path) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    _write_skill(root_a, "dup", name="shared", desc="first")
    _write_skill(root_b, "dup", name="shared", desc="second")
    skills = discover_skills([root_a, root_b])
    assert len(skills) == 1
    assert skills[0].description == "second"


def test_discover_skills_skips_malformed(tmp_path: Path) -> None:
    root = tmp_path / "r"
    _write_skill(root, "good", name="good")
    (root / "bad").mkdir()
    (root / "bad" / "SKILL.md").write_text("not a skill file", encoding="utf-8")
    skills = discover_skills([root])
    assert [s.name for s in skills] == ["good"]


def test_discover_skills_skips_missing_root(tmp_path: Path) -> None:
    real = tmp_path / "real"
    missing = tmp_path / "ghost"
    _write_skill(real, "x", name="x")
    skills = discover_skills([missing, real])
    assert [s.name for s in skills] == ["x"]


def test_discover_skills_empty_returns_empty_list(tmp_path: Path) -> None:
    assert discover_skills([tmp_path]) == []
