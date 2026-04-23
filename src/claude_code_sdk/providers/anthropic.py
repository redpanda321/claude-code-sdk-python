"""Anthropic Messages API provider.

Ports CCB ``src/services/api/claude.ts``. Streams SSE from
``POST {base_url}/v1/messages``.

Anti-regression (repo memory "Claude Code Anthropic runtime URL
normalization"): ``base_url`` must be the root host
(``https://api.anthropic.com``), **not** ``/v1``. The provider appends
``/v1/messages`` itself; passing ``/v1`` causes requests to hit
``/v1/v1/messages`` and return 404 ``not_found_error``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from .base import CompletionRequest, ProviderError, StreamEvent

__all__ = ["AnthropicProvider"]

_RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class AnthropicProvider:
    name = "anthropic"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        anthropic_version: str = "2023-06-01",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/v1"):
            raise ValueError(
                "Anthropic base_url must be root host, not /v1 "
                "(see repo memory: Claude Code Anthropic runtime URL normalization)"
            )
        self._api_key = api_key
        self._base_url = normalized
        self._version = anthropic_version
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        payload = req.model_dump(exclude_none=True)
        payload["stream"] = True
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self._version,
            "content-type": "application/json",
            "accept": "text/event-stream",
        }
        url = f"{self._base_url}/v1/messages"
        async with self._client.stream("POST", url, json=payload, headers=headers) as r:
            if r.status_code >= 400:
                body = (await r.aread()).decode("utf-8", errors="replace")
                raise ProviderError(
                    r.status_code,
                    body,
                    retryable=r.status_code in _RETRYABLE_STATUS,
                )
            event_name = ""
            async for line in r.aiter_lines():
                if not line:
                    continue
                if line.startswith("event:"):
                    event_name = line[6:].strip()
                elif line.startswith("data:"):
                    raw = line[5:].strip()
                    if not raw:
                        continue
                    data = json.loads(raw)
                    yield StreamEvent(
                        event=event_name or data.get("type", ""),
                        data=data,
                    )

    async def aclose(self) -> None:
        await self._client.aclose()
