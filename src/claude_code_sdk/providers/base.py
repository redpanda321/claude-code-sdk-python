"""Provider base types.

Ports CCB ``src/services/api/**`` shape into Python. All providers implement
the :class:`Provider` Protocol and stream :class:`StreamEvent` values from
``messages_stream``. No LiteLLM / CAMEL dependency (CONTEXT D-05, D-18).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "CompletionRequest",
    "Message",
    "Provider",
    "ProviderError",
    "StreamEvent",
]


class Message(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict[str, Any]]


class CompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    messages: list[Message]
    max_tokens: int = 4096
    temperature: float | None = None
    stream: bool = True
    tools: list[dict[str, Any]] = Field(default_factory=list[dict[str, Any]])
    metadata: dict[str, Any] = Field(default_factory=dict[str, Any])


class StreamEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: str
    data: dict[str, Any] = Field(default_factory=dict[str, Any])


class ProviderError(RuntimeError):
    """Raised on HTTP / SDK errors from a vendor backend."""

    def __init__(self, status: int, body: str, *, retryable: bool = False) -> None:
        super().__init__(f"Provider error {status}: {body[:200]}")
        self.status = status
        self.body = body
        self.retryable = retryable


@runtime_checkable
class Provider(Protocol):
    name: str

    def messages_stream(self, req: CompletionRequest) -> AsyncIterator[StreamEvent]: ...

    async def aclose(self) -> None: ...
