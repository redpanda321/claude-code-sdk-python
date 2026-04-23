"""Memory-directory type schemas (Pydantic v2).

Ports CCB ``src/memdir/memoryTypes.ts``. Uses concrete ``pathlib.Path`` for
``MemoryEntry.path`` per the project STATE.md decision (not PurePosixPath).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

MemoryScope = Literal["user", "project", "session"]


class MemoryEntry(BaseModel):
    """A single memory file discovered on disk."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    scope: MemoryScope
    path: Path
    name: str
    content: str
