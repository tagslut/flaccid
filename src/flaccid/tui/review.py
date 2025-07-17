"""Interactive metadata review utilities."""

from __future__ import annotations

from dataclasses import asdict

from prompt_toolkit.shortcuts import radiolist_dialog

from flaccid.plugins.base import TrackMetadata


def review_metadata(meta: TrackMetadata) -> TrackMetadata:
    """Return a new :class:`TrackMetadata` after interactive review.

    Each field of ``meta`` is presented to the user with a simple dialog using
    arrow key navigation to choose whether to keep or drop the value. Dropped
    fields are returned as ``None`` in the resulting object.
    """

    data = asdict(meta)
    result: dict[str, object] = {}
    for field, value in data.items():
        if value in (None, ""):
            result[field] = value
            continue
        choice = radiolist_dialog(
            title=f"{field}",
            text=f"{field}: {value}\nKeep this value?",
            values=[("keep", "Keep"), ("drop", "Drop")],
        ).run()
        result[field] = value if choice == "keep" else None
    return TrackMetadata(**result)  # type: ignore[arg-type]
