"""Skill discovery + SKILL.md frontmatter parsing.

Ports CCB ``src/skills/**`` per CONTEXT D-19 (full-parity surface).
"""

from __future__ import annotations

from .discovery import discover_skills
from .parser import Skill, SkillParseError, parse_skill, parse_skill_text

__all__ = [
    "Skill",
    "SkillParseError",
    "discover_skills",
    "parse_skill",
    "parse_skill_text",
]
