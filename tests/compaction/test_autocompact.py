from __future__ import annotations

from collections.abc import AsyncIterator

from claude_code_sdk.compaction import autocompact_if_needed, estimate_tokens
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


def test_estimate_tokens_char_div_4() -> None:
    msgs = [Message(role="user", content="hello" * 4)]  # 20 chars → 5 tokens
    assert estimate_tokens(msgs) == 5


def test_estimate_tokens_handles_list_content() -> None:
    msgs = [
        Message(
            role="user",
            content=[{"type": "text", "text": "abcd"}, {"type": "text", "text": "efgh"}],
        )
    ]  # 8 chars → 2 tokens
    assert estimate_tokens(msgs) == 2


async def test_under_budget_short_circuits() -> None:
    provider = FakeProvider(deltas=["x"])
    msgs = [Message(role="user", content="hello")]
    out = await autocompact_if_needed(msgs, token_budget=1000, provider=provider)
    assert out == msgs
    assert provider.calls == []


async def test_over_budget_delegates_to_microcompact() -> None:
    provider = FakeProvider(deltas=["Sum"])
    msgs: list[Message] = [Message(role="user", content="x" * 100) for _ in range(20)]
    out = await autocompact_if_needed(msgs, token_budget=10, provider=provider, keep_tail=3)
    # microcompact produced: summary + 3 tail
    assert len(out) == 4
    assert out[0].role == "system"
    assert len(provider.calls) == 1
