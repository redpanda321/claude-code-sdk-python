from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from claude_code_sdk.plugins import PluginManifest, load_manifest


def test_load_manifest_round_trip(tmp_path: Path) -> None:
    data = {
        "name": "hello",
        "version": "1.2.3",
        "description": "say hi",
        "hooks": [{"event": "pre_tool_use", "handler": "hello.main:handler"}],
        "commands": [{"name": "hi", "handler": "hello.main:cmd"}],
        "skills": ["hello-skill"],
    }
    path = tmp_path / "plugin.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    manifest = load_manifest(path)
    assert isinstance(manifest, PluginManifest)
    assert manifest.name == "hello"
    assert manifest.version == "1.2.3"
    assert manifest.hooks[0].event == "pre_tool_use"
    assert manifest.commands[0].name == "hi"
    assert manifest.skills == ["hello-skill"]


def test_load_manifest_defaults(tmp_path: Path) -> None:
    path = tmp_path / "plugin.json"
    path.write_text(json.dumps({"name": "mini"}), encoding="utf-8")
    manifest = load_manifest(path)
    assert manifest.version == "0.0.0"
    assert manifest.hooks == []
    assert manifest.commands == []


def test_load_manifest_rejects_missing_name(tmp_path: Path) -> None:
    path = tmp_path / "plugin.json"
    path.write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_manifest(path)


def test_hook_spec_forbids_extra_fields() -> None:
    from claude_code_sdk.plugins import PluginHookSpec

    with pytest.raises(ValidationError):
        PluginHookSpec(event="pre_tool_use", handler="mod:h", extra="nope")  # type: ignore[call-arg]
