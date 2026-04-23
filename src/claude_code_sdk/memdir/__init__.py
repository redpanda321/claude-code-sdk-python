"""memdir -- Memory-directory loader for AGENTS.md / CLAUDE.md / *.md.

Ported from CCB ``src/memdir/**`` + ``src/memory/**``. Shape mirrors
``claude-code-sdk-ts/src/memdir/index.ts``.
"""

from __future__ import annotations

from .loader import load_memories, walk_up
from .types import MemoryEntry, MemoryScope

__all__ = [
    "MemoryEntry",
    "MemoryScope",
    "load_memories",
    "walk_up",
]
