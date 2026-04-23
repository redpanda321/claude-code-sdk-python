from __future__ import annotations

import httpx
import pytest

from claude_code_sdk.providers import AnthropicProvider, CompletionRequest, Message


def _sse_response(body: str) -> httpx.Response:
    return httpx.Response(
        200,
        content=body.encode(),
        headers={"content-type": "text/event-stream"},
    )


def test_v1_base_url_rejected() -> None:
    with pytest.raises(ValueError, match="must be root host"):
        AnthropicProvider(api_key="k", base_url="https://api.anthropic.com/v1")


def test_v1_base_url_rejected_trailing_slash() -> None:
    with pytest.raises(ValueError):
        AnthropicProvider(api_key="k", base_url="https://api.anthropic.com/v1/")


async def test_stream_yields_events() -> None:
    body = (
        "event: message_start\n"
        'data: {"type":"message_start"}\n'
        "\n"
        "event: content_block_delta\n"
        'data: {"type":"content_block_delta","delta":{"text":"hi"}}\n'
        "\n"
        "event: message_stop\n"
        'data: {"type":"message_stop"}\n'
        "\n"
    )

    captured: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["req"] = request
        return _sse_response(body)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    p = AnthropicProvider(api_key="k", client=client)
    req = CompletionRequest(
        model="claude-sonnet-4",
        messages=[Message(role="user", content="hi")],
    )
    events = [e.event async for e in p.messages_stream(req)]
    assert events == ["message_start", "content_block_delta", "message_stop"]
    assert str(captured["req"].url) == "https://api.anthropic.com/v1/messages"
    assert captured["req"].headers["x-api-key"] == "k"
    assert captured["req"].headers["anthropic-version"] == "2023-06-01"
    await p.aclose()


async def test_error_status_raises_provider_error() -> None:
    from claude_code_sdk.providers import ProviderError

    transport = httpx.MockTransport(
        lambda req: httpx.Response(429, content=b'{"error":"rate_limited"}')
    )
    client = httpx.AsyncClient(transport=transport)
    p = AnthropicProvider(api_key="k", client=client)
    req = CompletionRequest(model="claude-sonnet-4", messages=[Message(role="user", content="hi")])
    with pytest.raises(ProviderError) as exc_info:
        async for _ in p.messages_stream(req):
            pass
    assert exc_info.value.status == 429
    assert exc_info.value.retryable is True
    await p.aclose()
