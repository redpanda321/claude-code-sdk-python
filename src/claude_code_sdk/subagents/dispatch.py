"""Subagent dispatcher -- name-indexed registry + streaming runner.

Ports the runtime half of CCB's ``src/tools/AgentTool/forkSession.ts``.
Multi-turn tool_use recovery, cost tracking, and hook dispatch inside
the subagent loop are deferred to a follow-up plan (see 999.2-14 SUMMARY).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from typing import Any, cast

from claude_code_sdk.providers import CompletionRequest, Message, Provider

from .definition import SubagentDefinition, SubagentDispatchError, SubagentEvent

__all__ = ["SubagentDispatcher", "SubagentRunResult"]


@dataclass(slots=True)
class SubagentRunResult:
    events: list[SubagentEvent]
    final_text: str


class SubagentDispatcher:
    """Name-indexed subagent registry + async runner."""

    def __init__(
        self,
        provider: Provider,
        tools: Mapping[str, Any],
    ) -> None:
        self._provider = provider
        self._tools: dict[str, Any] = dict(tools)
        self._subagents: dict[str, SubagentDefinition] = {}

    def register(self, definition: SubagentDefinition) -> None:
        missing = [t for t in definition.tools if t not in self._tools]
        if missing:
            raise SubagentDispatchError(
                f"subagent {definition.name!r} references unknown tools: {missing}"
            )
        self._subagents[definition.name] = definition

    def resolve(self, name: str) -> SubagentDefinition:
        if name not in self._subagents:
            raise SubagentDispatchError(f"subagent not registered: {name}")
        return self._subagents[name]

    async def run(self, name: str, prompt: str) -> AsyncIterator[SubagentEvent]:
        subagent = self.resolve(name)
        req = CompletionRequest(
            model=subagent.model,
            messages=[
                Message(role="system", content=subagent.system_prompt),
                Message(role="user", content=prompt),
            ],
        )
        collected_text: list[str] = []
        async for ev in self._provider.messages_stream(req):
            if ev.event == "content_block_delta":
                delta = cast("dict[str, Any]", ev.data.get("delta") or {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    if isinstance(text, str):
                        collected_text.append(text)
            yield SubagentEvent(kind="stream", data=ev.model_dump())
        yield SubagentEvent(kind="final", data={"text": "".join(collected_text)})
