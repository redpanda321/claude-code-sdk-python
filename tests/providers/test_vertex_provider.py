from __future__ import annotations

import sys
from typing import Any

import httpx
import pytest

from claude_code_sdk.providers import CompletionRequest, Message, VertexProvider


async def test_missing_google_auth_raises_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "google.auth", None)
    monkeypatch.setitem(sys.modules, "google", None)
    p = VertexProvider(project_id="p", location="us-central1")
    req = CompletionRequest(
        model="claude-sonnet-4@20250514",
        messages=[Message(role="user", content="hi")],
    )
    with pytest.raises(ImportError, match=r"claude-code-sdk\[vertex\]"):
        async for _ in p.messages_stream(req):
            pass


async def test_happy_path_with_stubbed_credentials() -> None:
    body = (
        "event: message_start\n"
        'data: {"type":"message_start"}\n'
        "\n"
        "event: message_stop\n"
        'data: {"type":"message_stop"}\n'
        "\n"
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

    class StubCreds:
        token = "stub-token"

        def refresh(self, _request: Any) -> None:
            pass

    p = VertexProvider(
        project_id="proj",
        location="us-central1",
        client=client,
        credentials=StubCreds(),
    )
    req = CompletionRequest(
        model="claude-sonnet-4@20250514",
        messages=[Message(role="user", content="hi")],
    )
    events = [e.event async for e in p.messages_stream(req)]
    assert events == ["message_start", "message_stop"]
    assert "us-central1-aiplatform.googleapis.com" in captured["url"]
    assert captured["auth"] == "Bearer stub-token"
    await p.aclose()
