from __future__ import annotations

"""Tests for metadata.cascade."""

from flaccid.core import metadata
from flaccid.plugins.base import AlbumMetadata, TrackMetadata


def test_cascade_merges_track_metadata() -> None:
    first = TrackMetadata(
        title="One",
        artist="",
        album="A",
        track_number=1,
        disc_number=1,
        year=None,
        isrc=None,
    )
    second = TrackMetadata(
        title=None,
        artist="Artist",
        album=None,
        track_number=2,
        disc_number=1,
        year=2024,
        isrc="XYZ",
    )

    merged = metadata.cascade(first, second)

    assert merged.title == "One"
    assert merged.artist == "Artist"
    assert merged.album == "A"
    assert merged.track_number == 1
    assert merged.year == 2024
    assert merged.isrc == "XYZ"


def test_cascade_order_matters() -> None:
    a = TrackMetadata(
        title="A",
        artist="a",
        album="X",
        track_number=1,
        disc_number=1,
    )
    b = TrackMetadata(
        title="B",
        artist="b",
        album="Y",
        track_number=2,
        disc_number=1,
    )

    left = metadata.cascade(a, b)
    right = metadata.cascade(b, a)

    assert left.title == "A"
    assert right.title == "B"


def test_cascade_album_metadata() -> None:
    first = AlbumMetadata(title="", artist="X")
    second = AlbumMetadata(title="Best", artist="Y", year=2024, cover_url="u")

    merged = metadata.cascade(first, second)

    assert merged.title == "Best"
    assert merged.artist == "X"
    assert merged.year == 2024
    assert merged.cover_url == "u"
