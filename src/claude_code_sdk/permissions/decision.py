"""Permission rule parser + single-rule matching.

Ports CCB permission-rule shape. ``PermissionResult`` is re-exported from
:mod:`claude_code_sdk.tools` -- **never** redefine it here.
"""

from __future__ import annotations

import fnmatch
import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from claude_code_sdk.tools import PermissionResult

__all__ = ["PermissionResult", "PermissionRule", "match_rule", "parse_rule"]


_PRIMARY_FIELDS: dict[str, str] = {
    "Bash": "command",
    "Read": "path",
    "Write": "path",
    "Edit": "path",
    "Glob": "pattern",
    "Grep": "pattern",
}
_RULE_RE = re.compile(r"^(?P<tool>[A-Za-z_][\w]*)(?:\((?P<pattern>.*)\))?$")


class PermissionRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    pattern: str | None = None

    @property
    def field(self) -> str:
        return _PRIMARY_FIELDS.get(self.tool, "command")


def parse_rule(text: str) -> PermissionRule:
    """Parse ``Tool`` or ``Tool(glob)`` syntax into a :class:`PermissionRule`."""
    m = _RULE_RE.match(text.strip())
    if not m:
        raise ValueError(f"invalid permission rule: {text!r}")
    return PermissionRule(tool=m.group("tool"), pattern=m.group("pattern"))


def match_rule(rule: PermissionRule, tool_name: str, input_dict: dict[str, Any]) -> bool:
    """Return True iff ``rule`` matches a tool invocation."""
    if rule.tool != tool_name:
        return False
    if rule.pattern is None:
        return True
    value = str(input_dict.get(rule.field, ""))
    return fnmatch.fnmatchcase(value, rule.pattern)
