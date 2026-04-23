from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from claude_code_sdk.providers import CompletionRequest, StreamEvent
from claude_code_sdk.subagents import (
    SubagentDefinition,
    SubagentDispatcher,
    SubagentDispatchError,
)


class FakeProvider:
    name = "fake"

    def __init__(self, deltas: list[str]) -> None:
        self._deltas = deltas
        self.last_request: CompletionRequest | None = None

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        self.last_request = req
        yield StreamEvent(event="message_start", data={"type": "message_start"})
        for chunk in self._deltas:
            yield StreamEvent(
                event="content_block_delta",
                data={"delta": {"type": "text_delta", "text": chunk}},
            )
        yield StreamEvent(event="message_stop", data={"type": "message_stop"})

    async def aclose(self) -> None:
        return None


class FakeTool:
    # Minimal Tool-shaped stub (name-only lookup used by dispatcher register()).
    name = "Read"

    def __init__(self, name: str) -> None:
        self.name = name


def test_register_accepts_known_tools() -> None:
    provider = FakeProvider([])
    tools: dict[str, Any] = {"Read": FakeTool("Read"), "Grep": FakeTool("Grep")}
    dispatcher = SubagentDispatcher(provider=provider, tools=tools)
    dispatcher.register(SubagentDefinition(name="r", tools=["Read", "Grep"]))
    assert dispatcher.resolve("r").name == "r"


def test_register_rejects_unknown_tools() -> None:
    provider = FakeProvider([])
    dispatcher = SubagentDispatcher(provider=provider, tools={})
    with pytest.raises(SubagentDispatchError, match="unknown tools"):
        dispatcher.register(SubagentDefinition(name="r", tools=["Bogus"]))


def test_resolve_unknown_subagent_raises() -> None:
    provider = FakeProvider([])
    dispatcher = SubagentDispatcher(provider=provider, tools={})
    with pytest.raises(SubagentDispatchError, match="not registered"):
        dispatcher.resolve("missing")


async def test_run_streams_events_and_emits_final() -> None:
    provider = FakeProvider(deltas=["he", "llo"])
    dispatcher = SubagentDispatcher(provider=provider, tools={})
    dispatcher.register(SubagentDefinition(name="r", system_prompt="be helpful"))
    events = [ev async for ev in dispatcher.run("r", "say hi")]
    # 4 stream events (start + 2 deltas + stop) + 1 final
    assert len(events) == 5
    assert events[-1].kind == "final"
    assert events[-1].data == {"text": "hello"}
    assert all(e.kind == "stream" for e in events[:-1])
    assert provider.last_request is not None
    assert provider.last_request.messages[0].role == "system"
    assert provider.last_request.messages[0].content == "be helpful"
    assert provider.last_request.messages[1].content == "say hi"
