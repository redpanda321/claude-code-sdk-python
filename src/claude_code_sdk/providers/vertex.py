"""Google Vertex AI provider (Anthropic models on Vertex).

Lazy-imports ``google.auth`` so the module imports cleanly without the
``vertex`` extra. Uses :class:`httpx.AsyncClient` for SSE streaming.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, cast

import httpx

from .base import CompletionRequest, ProviderError, StreamEvent

__all__ = ["VertexProvider"]

_INSTALL_HINT = (
    "claude-code-sdk[vertex] extra required -- install via pip install 'claude-code-sdk[vertex]'"
)
_RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class VertexProvider:
    name = "vertex"

    def __init__(
        self,
        project_id: str,
        location: str,
        *,
        client: httpx.AsyncClient | None = None,
        credentials: Any | None = None,
    ) -> None:
        self._project_id = project_id
        self._location = location
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))
        self._credentials: Any | None = credentials

    def _resolve_credentials(self) -> Any:
        if self._credentials is not None:
            return self._credentials
        try:
            import google.auth  # type: ignore[import-not-found]
            import google.auth.transport.requests  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as exc:
            raise ImportError(_INSTALL_HINT) from exc
        if google.auth is None:  # test hook
            raise ImportError(_INSTALL_HINT)
        creds_tuple = cast(
            "tuple[Any, Any]",
            google.auth.default(  # pyright: ignore[reportUnknownMemberType]
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            ),
        )
        creds = creds_tuple[0]
        self._credentials = creds
        return creds

    async def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]:
        creds = self._resolve_credentials()
        # Refresh token if the credentials object supports it.
        try:
            import google.auth.transport.requests as _gar  # type: ignore[import-not-found]

            creds.refresh(_gar.Request())
        except ImportError:
            # Stubbed credentials in tests: call refresh with a sentinel.
            creds.refresh(None)
        token = getattr(creds, "token", None) or ""

        url = (
            f"https://{self._location}-aiplatform.googleapis.com/v1/projects/"
            f"{self._project_id}/locations/{self._location}/publishers/anthropic/"
            f"models/{req.model}:streamRawPredict"
        )
        payload = req.model_dump(exclude_none=True)
        payload.setdefault("anthropic_version", "vertex-2023-10-16")
        headers = {
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "accept": "text/event-stream",
        }
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
