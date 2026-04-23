"""Plugin discovery + loader surface.

Ports CCB ``src/plugins/**`` + the plugin-side of
``src/utils/hooks/registerHook.ts`` per CONTEXT D-19.
"""

from __future__ import annotations

from .loader import LoadedPlugin, PluginLoader, PluginLoadError
from .manifest import PluginCommandSpec, PluginHookSpec, PluginManifest, load_manifest

__all__ = [
    "LoadedPlugin",
    "PluginCommandSpec",
    "PluginHookSpec",
    "PluginLoadError",
    "PluginLoader",
    "PluginManifest",
    "load_manifest",
]
