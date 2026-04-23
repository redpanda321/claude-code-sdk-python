from __future__ import annotations

from claude_code_sdk.providers import (
    CompletionRequest,
    Message,
    Provider,
    ProviderError,
    StreamEvent,
)


def test_message_roles() -> None:
    m = Message(role="user", content="hi")
    assert m.role == "user"
    assert m.content == "hi"


def test_completion_request_defaults() -> None:
    req = CompletionRequest(model="claude-sonnet-4", messages=[Message(role="user", content="hi")])
    assert req.max_tokens == 4096
    assert req.stream is True
    assert req.tools == []
    assert req.metadata == {}


def test_stream_event_round_trip() -> None:
    ev = StreamEvent(event="message_start", data={"type": "message_start"})
    dumped = ev.model_dump()
    again = StreamEvent.model_validate(dumped)
    assert again.event == "message_start"
    assert again.data == {"type": "message_start"}


def test_provider_error_flags() -> None:
    e = ProviderError(429, "rate limited", retryable=True)
    assert e.status == 429
    assert e.body == "rate limited"
    assert e.retryable is True


def test_provider_protocol_is_runtime_checkable() -> None:
    class Dummy:
        name = "dummy"

        async def messages_stream(self, req):  # type: ignore[no-untyped-def]
            if False:
                yield

        async def aclose(self) -> None:
            pass

    assert isinstance(Dummy(), Provider)
