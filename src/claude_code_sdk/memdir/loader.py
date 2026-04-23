"""Memory-directory loader -- walks up from cwd collecting AGENTS.md/CLAUDE.md.

Ports CCB ``src/memdir/memdir.ts`` + ``memoryScan.ts`` + ``paths.ts``.

Scans each ancestor of ``cwd`` for top-level memory files and any ``*.md``
under the per-project memory subdirectories, then appends user-scoped
entries from ``extra_roots``. Dedupes by ``(scope, name)`` with the last
encountered entry winning (per plan 13 contract).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from .types import MemoryEntry, MemoryScope

_TOP_LEVEL_FILES: tuple[str, ...] = ("CLAUDE.md", "AGENTS.md")
_MEMORY_SUBDIRS: tuple[str, ...] = (".claude/memories", ".claude", "memories")


def walk_up(start: Path) -> Iterator[Path]:
    """Yield ``start`` (resolved) then each parent up to the filesystem root."""
    current = start.resolve()
    yield current
    yield from current.parents


def _scan_dir(root: Path, scope: MemoryScope) -> list[MemoryEntry]:
    entries: list[MemoryEntry] = []
    for name in _TOP_LEVEL_FILES:
        p = root / name
        if p.is_file():
            entries.append(
                MemoryEntry(
                    scope=scope,
                    path=p,
                    name=p.stem,
                    content=p.read_text(encoding="utf-8"),
                )
            )
    for sub in _MEMORY_SUBDIRS:
        d = root / sub
        if not d.is_dir():
            continue
        for md in sorted(d.glob("*.md")):
            entries.append(
                MemoryEntry(
                    scope=scope,
                    path=md,
                    name=md.stem,
                    content=md.read_text(encoding="utf-8"),
                )
            )
    return entries


def load_memories(
    cwd: Path,
    *,
    extra_roots: Iterable[Path] = (),
) -> list[MemoryEntry]:
    """Collect memory entries by walking up from ``cwd``.

    Args:
        cwd: Starting directory; scanned along with all of its ancestors.
        extra_roots: Additional roots (e.g. ``~/.claude``) scanned with
            ``scope="user"``.

    Returns:
        List of :class:`MemoryEntry`. Duplicates by ``(scope, name)`` are
        resolved with the last encountered entry winning.
    """
    seen: dict[tuple[str, str], MemoryEntry] = {}
    for root in walk_up(cwd):
        for entry in _scan_dir(root, "project"):
            seen[(entry.scope, entry.name)] = entry
    for root in extra_roots:
        for entry in _scan_dir(Path(root), "user"):
            seen[(entry.scope, entry.name)] = entry
    return list(seen.values())
