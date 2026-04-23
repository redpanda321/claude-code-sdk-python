"""Tests for claude_code_sdk.mcp Pydantic v2 type schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_sdk.mcp import (
    McpCallResult,
    McpServerSpec,
    McpToolRef,
)


def test_server_spec_stdio_defaults() -> None:
    s = McpServerSpec(name="echo", command="echo-srv", args=["--port", "1"])
    assert s.transport == "stdio"
    dumped = s.model_dump()
    assert dumped["args"] == ["--port", "1"]
    assert dumped["headers"] == {}
    assert dumped["env"] == {}


def test_server_spec_sse_round_trip() -> None:
    s = McpServerSpec(
        name="remote",
        transport="sse",
        url="https://example.com/mcp",
        headers={"Authorization": "Bearer x"},
    )
    roundtrip = McpServerSpec.model_validate(s.model_dump())
    assert roundtrip == s


def test_server_spec_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        McpServerSpec.model_validate({"name": "x", "bogus": True})


def test_tool_ref_ignores_unknown_fields() -> None:
    t = McpToolRef.model_validate(
        {
            "server": "s",
            "name": "t",
            "description": "d",
            "input_schema": {"type": "object"},
            "extra": 123,
        }
    )
    assert t.server == "s"
    assert t.name == "t"
    assert t.input_schema == {"type": "object"}


def test_call_result_defaults() -> None:
    r = McpCallResult()
    assert r.is_error is False
    assert r.content == []
