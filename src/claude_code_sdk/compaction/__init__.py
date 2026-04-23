"""Compaction trio.

Ported from CCB ``src/services/compact/**`` per CONTEXT D-19.
"""

from __future__ import annotations

from .autocompact import autocompact_if_needed, estimate_tokens
from .microcompact import microcompact
from .snip import snip_compact

__all__ = [
    "autocompact_if_needed",
    "estimate_tokens",
    "microcompact",
    "snip_compact",
]
