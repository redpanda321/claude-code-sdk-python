from __future__ import annotations

from typing import Any

import httpx

from claude_code_sdk.providers import CompletionRequest, GlmProvider, Message, OpenAICompatProvider


def test_glm_is_openai_compat_subclass() -> None:
    assert issubclass(GlmProvider, OpenAICompatProvider)


def test_glm_defaults_to_zhipu_base_url() -> None:
    p = GlmProvider(api_key="k")
    assert p._base_url == "https://open.bigmodel.cn/api/paas/v4"  # noqa: SLF001


async def test_glm_posts_to_zhipu_endpoint() -> None:
    body = 'data: {"choices":[{"delta":{"content":"ni"}}]}\n\ndata: [DONE]\n\n'
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(
            200, content=body.encode(), headers={"content-type": "text/event-stream"}
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    p = GlmProvider(api_key="k", client=client)
    req = CompletionRequest(model="glm-4", messages=[Message(role="user", content="你好")])
    events = [e async for e in p.messages_stream(req)]
    assert len(events) == 1
    assert captured["url"] == "https://open.bigmodel.cn/api/paas/v4/v1/chat/completions"
    await p.aclose()
