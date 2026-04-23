from __future__ import annotations

from typing import Any

import httpx
import pytest

from claude_code_sdk.providers import (
    CompletionRequest,
    Message,
    OpenAICompatProvider,
    ProviderError,
)


async def test_stream_yields_events_until_done() -> None:
    body = (
        'data: {"choices":[{"delta":{"content":"he"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"llo"}}]}\n\n'
        "data: [DONE]\n\n"
    )
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        return httpx.Response(
            200, content=body.encode(), headers={"content-type": "text/event-stream"}
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    p = OpenAICompatProvider(api_key="sk-test", base_url="https://api.example.com", client=client)
    req = CompletionRequest(
        model="gpt-4o",
        messages=[Message(role="user", content="hi")],
    )
    events = [e async for e in p.messages_stream(req)]
    # Two content chunks; [DONE] is consumed as sentinel, not emitted.
    assert len(events) == 2
    assert captured["url"] == "https://api.example.com/v1/chat/completions"
    assert captured["auth"] == "Bearer sk-test"
    await p.aclose()


async def test_error_status_raises_provider_error() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(500, content=b'{"error":"oops"}'))
    client = httpx.AsyncClient(transport=transport)
    p = OpenAICompatProvider(api_key="sk", base_url="https://api.example.com", client=client)
    req = CompletionRequest(model="gpt-4o", messages=[Message(role="user", content="hi")])
    with pytest.raises(ProviderError) as exc_info:
        async for _ in p.messages_stream(req):
            pass
    assert exc_info.value.status == 500
    assert exc_info.value.retryable is True
    await p.aclose()
