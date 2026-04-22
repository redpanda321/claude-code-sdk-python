"""claude-code-sdk -- Python port of claude-code (CCB).

Public-API-parity sibling of claude-code-sdk-ts (Phase 999.1).
Subpackages (populated in follow-up plans and phases):
    adapters, tools, mcp, providers, hooks, plugins, skills,
    commands, memdir, subagents, permissions, compaction
"""

from __future__ import annotations

try:
    from ._version import __version__
except ImportError:  # pragma: no cover - pre-build
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
