"""Metadata merge helpers."""

from __future__ import annotations

from dataclasses import asdict, fields
from typing import Iterable

from flaccid.core.config import Settings, get_precedence_order
from flaccid.plugins.base import TrackMetadata

__all__ = [
    "cascade",
    "cascade_with_provenance",
    "merge_by_precedence",
]


def cascade(
    *sources: TrackMetadata,
    strategies: dict[str, str] | None = None,
) -> TrackMetadata:
    """Merge metadata objects using optional per-field strategies."""

    if not sources:
        raise ValueError("at least one metadata object is required")

    merged = TrackMetadata(**asdict(sources[0]))
    strategies = strategies or {}
    for src in sources[1:]:
        for field in fields(TrackMetadata):
            val = getattr(merged, field.name)
            other = getattr(src, field.name)
            if other in (None, ""):
                continue

            strategy = strategies.get(field.name, "prefer")

            if strategy == "replace":
                setattr(merged, field.name, other)
            elif strategy == "append":
                if val in (None, ""):
                    setattr(merged, field.name, other)
                elif isinstance(val, str) and isinstance(other, str):
                    setattr(merged, field.name, val + other)
            else:  # prefer
                if val in (None, ""):
                    setattr(merged, field.name, other)
    return merged


def cascade_with_provenance(
    *sources: TrackMetadata,
    strategies: dict[str, str] | None = None,
) -> tuple[TrackMetadata, dict[str, str]]:
    """Merge ``sources`` and record the provider for each field."""

    merged = cascade(*sources, strategies=strategies)
    provenance: dict[str, str] = {}
    strategies = strategies or {}
    for field in fields(TrackMetadata):
        for src in reversed(sources):
            val = getattr(src, field.name)
            if val in (None, ""):
                continue
            provenance[field.name] = src.source or "unknown"
            strategy = strategies.get(field.name, "prefer")
            if strategy == "append" and provenance.get(field.name) != src.source:
                prev = provenance[field.name]
                provenance[field.name] = f"{prev}+{src.source or 'unknown'}"
            break
    return merged, provenance


def merge_by_precedence(
    results: dict[str, TrackMetadata],
    *,
    strategies: dict[str, str] | None = None,
    settings: Settings | None = None,
) -> TrackMetadata:
    """Merge ``results`` respecting configured plugin precedence."""

    order = get_precedence_order(results.keys(), settings=settings)
    ordered = [results[name] for name in order]
    return cascade(*ordered, strategies=strategies)
