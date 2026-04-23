"""Tests for claude_code_sdk.hooks.HookRegistry register/unregister/dispatch."""

from __future__ import annotations

import pytest

from claude_code_sdk.hooks import (
    HookDecision,
    HookEvent,
    HookNotFoundError,
    HookPayload,
    HookRegistry,
)


class _Handler:
    """Minimal class-based async handler exposing `.event` for the Protocol."""

    def __init__(self, event: HookEvent, decision: HookDecision) -> None:
        self.event: HookEvent = event
        self._decision = decision
        self.calls: int = 0

    async def __call__(self, payload: HookPayload) -> HookDecision:
        self.calls += 1
        return self._decision


def _payload(event: HookEvent = "pre_tool_use") -> HookPayload:
    return HookPayload(event=event, session_id="s", cwd="/tmp")


async def test_register_and_dispatch_all_allow_returns_allow() -> None:
    r = HookRegistry()
    h1 = _Handler("pre_tool_use", HookDecision(action="allow"))
    h2 = _Handler("pre_tool_use", HookDecision(action="allow"))
    r.register(h1)
    r.register(h2)
    d = await r.dispatch(_payload())
    assert d.action == "allow"
    assert h1.calls == 1 and h2.calls == 1


async def test_dispatch_with_no_handlers_returns_allow() -> None:
    r = HookRegistry()
    d = await r.dispatch(_payload("notification"))
    assert d.action == "allow"


async def test_dispatch_block_short_circuits() -> None:
    r = HookRegistry()
    r.register(_Handler("pre_tool_use", HookDecision(action="allow")))
    r.register(_Handler("pre_tool_use", HookDecision(action="block", reason="nope")))
    r.register(_Handler("pre_tool_use", HookDecision(action="modify", modified={"x": 1})))
    d = await r.dispatch(_payload())
    assert d.action == "block"
    assert d.reason == "nope"


async def test_dispatch_modify_merges_in_registration_order() -> None:
    r = HookRegistry()
    r.register(_Handler("pre_tool_use", HookDecision(action="modify", modified={"a": 1, "b": 2})))
    r.register(_Handler("pre_tool_use", HookDecision(action="modify", modified={"b": 99, "c": 3})))
    d = await r.dispatch(_payload())
    assert d.action == "modify"
    assert d.modified == {"a": 1, "b": 99, "c": 3}


async def test_unregister_removes_handler() -> None:
    r = HookRegistry()
    h = _Handler("post_tool_use", HookDecision(action="allow"))
    r.register(h)
    assert r.list("post_tool_use") == [h]
    r.unregister(h)
    assert r.list("post_tool_use") == []


async def test_unregister_missing_raises() -> None:
    r = HookRegistry()
    h = _Handler("stop", HookDecision(action="allow"))
    with pytest.raises(HookNotFoundError):
        r.unregister(h)


async def test_dispatch_scopes_by_event() -> None:
    r = HookRegistry()
    pre = _Handler("pre_tool_use", HookDecision(action="block", reason="pre"))
    post = _Handler("post_tool_use", HookDecision(action="block", reason="post"))
    r.register(pre)
    r.register(post)
    d = await r.dispatch(_payload("post_tool_use"))
    assert d.action == "block"
    assert d.reason == "post"
    assert pre.calls == 0
    assert post.calls == 1
