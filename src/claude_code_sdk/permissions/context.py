"""ToolPermissionContext -- evaluates allow/deny/ask rule lists.

Precedence: deny > allow > ask; unmatched input yields ``ask`` with
reason ``"no matching rule"`` (matches CCB behaviour).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from claude_code_sdk.tools import PermissionResult

from .decision import PermissionRule, match_rule, parse_rule


class ToolPermissionContext(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    allow: list[PermissionRule] = Field(default_factory=list[PermissionRule])
    deny: list[PermissionRule] = Field(default_factory=list[PermissionRule])
    ask: list[PermissionRule] = Field(default_factory=list[PermissionRule])

    @classmethod
    def from_strings(
        cls,
        *,
        allow: Iterable[str] = (),
        deny: Iterable[str] = (),
        ask: Iterable[str] = (),
    ) -> ToolPermissionContext:
        return cls(
            allow=[parse_rule(s) for s in allow],
            deny=[parse_rule(s) for s in deny],
            ask=[parse_rule(s) for s in ask],
        )

    def decide(self, tool_name: str, input_dict: dict[str, Any]) -> PermissionResult:
        for r in self.deny:
            if match_rule(r, tool_name, input_dict):
                return PermissionResult(
                    decision="deny",
                    reason=f"matched deny rule {r.tool}({r.pattern or ''})",
                )
        for r in self.allow:
            if match_rule(r, tool_name, input_dict):
                return PermissionResult(decision="allow")
        for r in self.ask:
            if match_rule(r, tool_name, input_dict):
                return PermissionResult(decision="ask")
        return PermissionResult(decision="ask", reason="no matching rule")
