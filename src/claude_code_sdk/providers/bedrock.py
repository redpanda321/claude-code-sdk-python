"""AWS Bedrock provider (Anthropic models via ``invoke_model_with_response_stream``).

Lazy-imports ``boto3`` so that environments without the ``bedrock`` extra
can still import :mod:`claude_code_sdk.providers`.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, cast

from .base import CompletionRequest, StreamEvent

__all__ = ["BedrockProvider"]

_INSTALL_HINT = (
    "claude-code-sdk[bedrock] extra required -- install via pip install 'claude-code-sdk[bedrock]'"
)


class BedrockProvider:
    name = "bedrock"

    def __init__(self, region: str, client: Any | None = None) -> None:
        self._region = region
        self._client: Any | None = client

    def _resolve_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(_INSTALL_HINT) from exc
        if boto3 is None:  # test hook: monkeypatched to None
            raise ImportError(_INSTALL_HINT)
        self._client = cast(Any, boto3.client("bedrock-runtime", region_name=self._region))  # pyright: ignore[reportUnknownMemberType]
        return self._client

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        client = self._resolve_client()
        payload = req.model_dump(exclude_none=True)
        # Bedrock's Anthropic model expects `anthropic_version` in the body.
        payload.setdefault("anthropic_version", "bedrock-2023-05-31")
        response = client.invoke_model_with_response_stream(
            modelId=req.model,
            body=json.dumps(payload),
        )
        body = response.get("body", [])
        for chunk in body:
            inner = chunk.get("chunk", {}).get("bytes", b"")
            if not inner:
                continue
            data = json.loads(inner.decode("utf-8"))
            yield StreamEvent(event=data.get("type", ""), data=data)

    async def aclose(self) -> None:
        # boto3 clients don't require explicit close.
        return None
