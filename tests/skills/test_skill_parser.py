from __future__ import annotations

from pathlib import Path

import pytest

from claude_code_sdk.skills import Skill, SkillParseError, parse_skill, parse_skill_text

_VALID = """---
name: hello
description: Says hi
---
Body content here.
"""


def test_parse_valid_frontmatter_returns_skill() -> None:
    skill = parse_skill_text(_VALID)
    assert isinstance(skill, Skill)
    assert skill.name == "hello"
    assert skill.description == "Says hi"
    assert skill.body == "Body content here."
    assert skill.source is None
    assert skill.frontmatter["name"] == "hello"


def test_parse_missing_opener_raises() -> None:
    with pytest.raises(SkillParseError, match="missing YAML frontmatter opener"):
        parse_skill_text("no frontmatter here\nbody")


def test_parse_unterminated_frontmatter_raises() -> None:
    with pytest.raises(SkillParseError, match="unterminated frontmatter"):
        parse_skill_text("---\nname: foo\nno closer here\n")


def test_parse_missing_name_key_raises() -> None:
    text = "---\ndescription: no name\n---\nbody\n"
    with pytest.raises(SkillParseError, match="missing `name`"):
        parse_skill_text(text)


def test_parse_body_is_stripped() -> None:
    text = "---\nname: x\n---\n\n  body with padding  \n\n"
    skill = parse_skill_text(text)
    assert skill.body == "body with padding"


def test_parse_skill_reads_path(tmp_path: Path) -> None:
    p = tmp_path / "SKILL.md"
    p.write_text(_VALID, encoding="utf-8")
    skill = parse_skill(p)
    assert skill.name == "hello"
    assert skill.source == p


def test_parse_invalid_yaml_raises() -> None:
    text = "---\nname: x\n  bad: : indent\n---\nbody\n"
    with pytest.raises(SkillParseError, match="invalid YAML frontmatter"):
        parse_skill_text(text)
