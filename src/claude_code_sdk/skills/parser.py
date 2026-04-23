"""SKILL.md frontmatter parser for claude_code_sdk.

Ports CCB src/skills/bundledSkills.ts + frontmatter handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class SkillParseError(ValueError):
    """Raised when a SKILL.md file cannot be parsed."""


class Skill(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    name: str
    description: str = ""
    body: str = ""
    source: Path | None = None
    frontmatter: dict[str, Any] = Field(default_factory=dict[str, Any])


_FRONTMATTER_DELIM = "---"


def parse_skill_text(text: str, *, source: Path | None = None) -> Skill:
    """Parse SKILL.md text: YAML frontmatter between `---` delimiters, then body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FRONTMATTER_DELIM:
        raise SkillParseError(f"SKILL.md missing YAML frontmatter opener at {source}")
    try:
        end = lines.index(_FRONTMATTER_DELIM, 1)
    except ValueError as e:
        raise SkillParseError(f"SKILL.md unterminated frontmatter at {source}") from e
    try:
        raw: Any = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        raise SkillParseError(f"invalid YAML frontmatter at {source}: {e}") from e
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise SkillParseError(f"SKILL.md frontmatter must be a mapping at {source}")
    fm: dict[str, Any] = {str(k): v for k, v in raw.items()}  # type: ignore[misc]
    if "name" not in fm:
        raise SkillParseError(f"SKILL.md frontmatter missing `name` at {source}")
    body = "\n".join(lines[end + 1 :]).strip()
    return Skill(
        name=str(fm["name"]),
        description=str(fm.get("description", "")),
        body=body,
        source=source,
        frontmatter=fm,
    )


def parse_skill(path: Path) -> Skill:
    """Read `path` as a SKILL.md file and parse it."""
    return parse_skill_text(path.read_text(encoding="utf-8"), source=path)
