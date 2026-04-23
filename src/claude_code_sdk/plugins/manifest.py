"""Plugin manifest schema (``plugin.json``).

Ports the CCB plugin-manifest shape into Pydantic v2 models.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class PluginHookSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    handler: str  # ``"pkg.module:object"`` dotted path


class PluginCommandSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    handler: str


class PluginManifest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    version: str = "0.0.0"
    description: str = ""
    hooks: list[PluginHookSpec] = Field(default_factory=list[PluginHookSpec])
    commands: list[PluginCommandSpec] = Field(default_factory=list[PluginCommandSpec])
    skills: list[str] = Field(default_factory=list[str])


def load_manifest(path: Path) -> PluginManifest:
    """Read ``plugin.json`` at ``path`` and return a validated :class:`PluginManifest`."""
    with path.open("r", encoding="utf-8") as fh:
        return PluginManifest.model_validate(json.load(fh))
