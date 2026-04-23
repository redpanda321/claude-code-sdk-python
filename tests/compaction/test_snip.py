from __future__ import annotations

from claude_code_sdk.compaction import snip_compact
from claude_code_sdk.providers import Message


def test_under_limit_returns_new_list_identical() -> None:
    msgs = [
        Message(role="user", content="a"),
        Message(role="assistant", content="b"),
    ]
    out = snip_compact(msgs, max_messages=20)
    assert out == msgs
    assert out is not msgs  # new list


def test_over_limit_keeps_system_and_tail() -> None:
    msgs: list[Message] = [Message(role="system", content="sys")]
    for i in range(10):
        msgs.append(Message(role="user", content=f"u{i}"))
    out = snip_compact(msgs, max_messages=3)
    assert out[0].role == "system"
    assert [m.content for m in out[1:]] == ["u7", "u8", "u9"]
    assert len(out) == 4


def test_over_limit_no_system_messages() -> None:
    msgs = [Message(role="user", content=f"u{i}") for i in range(5)]
    out = snip_compact(msgs, max_messages=2)
    assert [m.content for m in out] == ["u3", "u4"]
