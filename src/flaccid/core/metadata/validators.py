"""Validation helpers for tag merging."""

from __future__ import annotations

from dataclasses import fields
from typing import Iterable

from flaccid.plugins.base import TrackMetadata

__all__ = ["validate_field_retention"]


def validate_field_retention(
    merged: TrackMetadata, sources: Iterable[TrackMetadata]
) -> None:
    """Ensure no populated field from ``sources`` was dropped during merging."""
    for field in fields(TrackMetadata):
        had_value = any(getattr(src, field.name) not in (None, "") for src in sources)
        if had_value and getattr(merged, field.name) in (None, ""):
            raise ValueError(f"Field {field.name} lost during merge")
