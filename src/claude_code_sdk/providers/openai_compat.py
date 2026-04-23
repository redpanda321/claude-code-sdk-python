"""OpenAI-compatible chat-completions provider.

Ports CCB's ``src/services/api/openaiCompat.ts`` shape. Streams SSE with
the OpenAI ``data: [DONE]`` sentinel.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from .base import CompletionRequest, ProviderError, StreamEvent

__all__ = ["OpenAICompatProvider"]

_RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class OpenAICompatProvider:
    name = "openai-compat"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        payload = req.model_dump(exclude_none=True)
        payload["stream"] = True
        headers = {
            "authorization": f"Bearer {self._api_key}",
            "content-type": "application/json",
            "accept": "text/event-stream",
        }
        url = f"{self._base_url}/v1/chat/completions"
        async with self._client.stream("POST", url, json=payload, headers=headers) as r:
            if r.status_code >= 400:
                body = (await r.aread()).decode("utf-8", errors="replace")
                raise ProviderError(
                    r.status_code,
                    body,
                    retryable=r.status_code in _RETRYABLE_STATUS,
                )
            async for line in r.aiter_lines():
                if not line:
                    continue
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if not raw or raw == "[DONE]":
                    if raw == "[DONE]":
                        return
                    continue
                data = json.loads(raw)
                yield StreamEvent(event=data.get("object", "chat.completion.chunk"), data=data)

    async def aclose(self) -> None:
        await self._client.aclose()
