from __future__ import annotations

import sys
from typing import Any

import pytest

from claude_code_sdk.providers import BedrockProvider, CompletionRequest, Message


async def test_missing_boto3_raises_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "boto3", None)
    p = BedrockProvider(region="us-east-1")
    req = CompletionRequest(
        model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[Message(role="user", content="hi")],
    )
    with pytest.raises(ImportError, match=r"claude-code-sdk\[bedrock\]"):
        async for _ in p.messages_stream(req):
            pass


async def test_happy_path_uses_injected_client() -> None:
    calls: dict[str, Any] = {}

    class FakeBody:
        def __iter__(self) -> Any:
            return iter(
                [
                    {"chunk": {"bytes": b'{"type":"message_start"}'}},
                    {"chunk": {"bytes": b'{"type":"message_stop"}'}},
                ]
            )

    class FakeClient:
        def invoke_model_with_response_stream(self, **kwargs: Any) -> dict[str, Any]:
            calls["kwargs"] = kwargs
            return {"body": FakeBody()}

    p = BedrockProvider(region="us-east-1", client=FakeClient())
    req = CompletionRequest(
        model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[Message(role="user", content="hi")],
    )
    events = [e.data.get("type") async for e in p.messages_stream(req)]
    assert events == ["message_start", "message_stop"]
    assert calls["kwargs"]["modelId"] == "anthropic.claude-3-5-sonnet-20240620-v1:0"
