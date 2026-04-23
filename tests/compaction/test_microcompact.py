from __future__ import annotations

from collections.abc import AsyncIterator

from claude_code_sdk.compaction import microcompact
from claude_code_sdk.providers import CompletionRequest, Message, StreamEvent


class FakeProvider:
    name = "fake"

    def __init__(self, deltas: list[str]) -> None:
        self._deltas = deltas
        self.calls: list[CompletionRequest] = []

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        self.calls.append(req)
        for chunk in self._deltas:
            yield StreamEvent(
                event="content_block_delta",
                data={"delta": {"type": "text_delta", "text": chunk}},
            )

    async def aclose(self) -> None:
        return None


async def test_under_keep_tail_returns_original() -> None:
    provider = FakeProvider(deltas=["x"])
    msgs = [Message(role="user", content=str(i)) for i in range(3)]
    out = await microcompact(msgs, provider, keep_tail=10)
    assert out == msgs
    assert provider.calls == []


async def test_summary_replaces_head() -> None:
    provider = FakeProvider(deltas=["Summary ", "text."])
    msgs: list[Message] = []
    for i in range(10):
        msgs.append(Message(role="user", content=f"msg{i}"))
    out = await microcompact(msgs, provider, keep_tail=3)
    # Result = [summary system message, msg7, msg8, msg9]
    assert len(out) == 4
    assert out[0].role == "system"
    assert isinstance(out[0].content, str)
    assert "Summary text." in out[0].content
    assert [m.content for m in out[1:]] == ["msg7", "msg8", "msg9"]
    assert len(provider.calls) == 1


async def test_leading_system_preserved() -> None:
    provider = FakeProvider(deltas=["S"])
    msgs: list[Message] = [Message(role="system", content="system prompt")]
    for i in range(10):
        msgs.append(Message(role="user", content=f"u{i}"))
    out = await microcompact(msgs, provider, keep_tail=3)
    # Expect leading system + summary + 3 tail
    assert out[0].role == "system"
    assert out[0].content == "system prompt"
    assert out[1].role == "system"  # summary
    assert [m.content for m in out[2:]] == ["u7", "u8", "u9"]
