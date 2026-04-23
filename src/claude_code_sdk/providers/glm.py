"""Zhipu GLM provider -- OpenAI-compatible at ``open.bigmodel.cn``."""

from __future__ import annotations

import httpx

from .openai_compat import OpenAICompatProvider

__all__ = ["GlmProvider"]

_ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"


class GlmProvider(OpenAICompatProvider):
    name = "glm"

    def __init__(
        self,
        api_key: str,
        base_url: str = _ZHIPU_BASE_URL,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, client=client)
