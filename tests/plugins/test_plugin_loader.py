from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from claude_code_sdk.hooks import HookDecision, HookPayload, HookRegistry
from claude_code_sdk.plugins import LoadedPlugin, PluginLoader, PluginLoadError

_PLUGIN_SRC = textwrap.dedent(
    """
    from claude_code_sdk.hooks import HookDecision

    class _Handler:
        event = "pre_tool_use"
        async def __call__(self, payload):
            return HookDecision(action="modify", modified={"from_plugin": True})

    handler = _Handler()
    """
).strip()


def _make_plugin(root: Path, pkg: str, *, extra_event: str | None = None) -> Path:
    plugin_dir = root / pkg
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
    src = _PLUGIN_SRC
    if extra_event is not None:
        src = src.replace('event = "pre_tool_use"', f'event = "{extra_event}"')
    (plugin_dir / "main.py").write_text(src, encoding="utf-8")
    manifest = {
        "name": pkg,
        "hooks": [{"event": extra_event or "pre_tool_use", "handler": f"{pkg}.main:handler"}],
    }
    (plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
    return plugin_dir


def test_discover_returns_loaded_plugins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(tmp_path))
    _make_plugin(tmp_path, "alpha")
    _make_plugin(tmp_path, "beta", extra_event="post_tool_use")
    plugins = PluginLoader.discover(tmp_path)
    names = sorted(p.manifest.name for p in plugins)
    assert names == ["alpha", "beta"]
    assert all(isinstance(p, LoadedPlugin) for p in plugins)
    assert all(len(p.hook_handlers) == 1 for p in plugins)


async def test_install_round_trip_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(tmp_path))
    _make_plugin(tmp_path, "gamma")
    plugins = PluginLoader.discover(tmp_path)
    registry = HookRegistry()
    PluginLoader.install(registry, plugins[0])
    decision = await registry.dispatch(
        HookPayload(event="pre_tool_use", session_id="s1", cwd="/tmp", data={})
    )
    assert isinstance(decision, HookDecision)
    assert decision.action == "modify"
    assert decision.modified == {"from_plugin": True}


def test_resolve_handler_missing_module_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(tmp_path))
    plugin_dir = tmp_path / "broken"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "name": "broken",
                "hooks": [{"event": "pre_tool_use", "handler": "does_not_exist:h"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(PluginLoadError, match="failed to resolve"):
        PluginLoader.discover(tmp_path)


def test_resolve_handler_without_event_attr_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(tmp_path))
    plugin_dir = tmp_path / "no_event"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugin_dir / "main.py").write_text("handler = 42\n", encoding="utf-8")
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "name": "no_event",
                "hooks": [{"event": "pre_tool_use", "handler": "no_event.main:handler"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(PluginLoadError, match="does not expose an `.event`"):
        PluginLoader.discover(tmp_path)


def test_discover_empty_root_returns_empty(tmp_path: Path) -> None:
    assert PluginLoader.discover(tmp_path) == []
