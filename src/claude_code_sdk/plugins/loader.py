"""Plugin loader: discovers ``plugin.json`` manifests and binds handlers.

Ports the CCB plugin loading flow (``src/plugins/builtinPlugins.ts`` +
``src/utils/hooks/registerHook.ts``). Handlers are resolved via
``importlib.import_module`` using a ``"pkg.module:object"`` dotted path.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path

from claude_code_sdk.hooks import HookHandler, HookRegistry

from .manifest import PluginManifest, load_manifest


class PluginLoadError(RuntimeError):
    """Raised when a plugin manifest references an unresolvable handler."""


@dataclass(slots=True)
class LoadedPlugin:
    manifest: PluginManifest
    root: Path
    hook_handlers: list[HookHandler] = field(default_factory=list[HookHandler])


class PluginLoader:
    """Stateless helpers that discover and install plugins."""

    @staticmethod
    def discover(root: Path) -> list[LoadedPlugin]:
        """Walk ``root`` for ``*/plugin.json`` and resolve each plugin's handlers."""
        if not root.is_dir():
            return []
        out: list[LoadedPlugin] = []
        for manifest_path in sorted(root.glob("*/plugin.json")):
            manifest = load_manifest(manifest_path)
            handlers = [
                PluginLoader._resolve_handler(manifest_path.parent, spec.handler)
                for spec in manifest.hooks
            ]
            out.append(
                LoadedPlugin(
                    manifest=manifest,
                    root=manifest_path.parent,
                    hook_handlers=handlers,
                )
            )
        return out

    @staticmethod
    def _resolve_handler(plugin_root: Path, dotted: str) -> HookHandler:
        del plugin_root  # reserved for future relative imports
        try:
            mod_name, _, attr = dotted.partition(":")
            if not mod_name or not attr:
                raise PluginLoadError(f"invalid dotted handler path {dotted!r}")
            mod = importlib.import_module(mod_name)
            handler = getattr(mod, attr)
        except PluginLoadError:
            raise
        except (ImportError, AttributeError) as e:
            raise PluginLoadError(f"failed to resolve {dotted}: {e}") from e
        if not hasattr(handler, "event"):
            raise PluginLoadError(f"{dotted} does not expose an `.event` attribute")
        return handler  # type: ignore[no-any-return]

    @staticmethod
    def install(registry: HookRegistry, plugin: LoadedPlugin) -> None:
        """Register every handler in ``plugin`` with ``registry``."""
        for h in plugin.hook_handlers:
            registry.register(h)
