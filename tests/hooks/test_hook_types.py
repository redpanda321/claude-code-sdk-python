"""Tests for claude_code_sdk.hooks Pydantic v2 schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_sdk.hooks import HookDecision, HookEvent, HookPayload


def test_hook_payload_accepts_all_seven_events() -> None:
    events: list[HookEvent] = [
        "pre_tool_use",
        "post_tool_use",
        "user_prompt_submit",
        "session_start",
        "session_end",
        "stop",
        "notification",
    ]
    for ev in events:
        p = HookPayload(event=ev, session_id="s", cwd="/tmp")
        assert p.event == ev
        assert p.data == {}


def test_hook_payload_rejects_unknown_event() -> None:
    with pytest.raises(ValidationError):
        HookPayload.model_validate({"event": "garbage", "session_id": "s", "cwd": "/tmp"})


def test_hook_decision_defaults_allow() -> None:
    d = HookDecision()
    assert d.action == "allow"
    assert d.reason is None
    assert d.modified is None


def test_hook_decision_block_with_reason() -> None:
    d = HookDecision(action="block", reason="denied")
    assert d.action == "block"
    assert d.reason == "denied"


def test_hook_decision_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        HookDecision.model_validate({"action": "allow", "bogus": True})
