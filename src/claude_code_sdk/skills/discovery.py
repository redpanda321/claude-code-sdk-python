"""Multi-root skill discovery. Ports CCB src/skills/loadSkillsDir.ts."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .parser import Skill, SkillParseError, parse_skill


def discover_skills(roots: Iterable[Path]) -> list[Skill]:
    """Walk each root for ``*/SKILL.md``; dedupe by skill name, last-writer-wins.

    Malformed SKILL.md files are silently skipped. Non-existent roots are also
    skipped. Iteration order is ``sorted(root.glob("*/SKILL.md"))`` within a
    root, so dedupe is deterministic across roots.
    """
    seen: dict[str, Skill] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            try:
                skill = parse_skill(skill_md)
            except SkillParseError:
                continue
            seen[skill.name] = skill
    return list(seen.values())
