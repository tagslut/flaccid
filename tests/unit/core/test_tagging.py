from __future__ import annotations

"""Tests for metadata tagging helpers."""

import unittest.mock
from pathlib import Path

import pytest

from flaccid.core import metadata
from flaccid.core.config import Settings
from flaccid.plugins.base import (
    LyricsProviderPlugin,
    MetadataProviderPlugin,
    TrackMetadata,
)


class FakeFLAC:
    """Simple mock of :class:`mutagen.flac.FLAC`."""

    def __init__(self, path):
        # print(f"FakeFLAC.__init__ called with path: {path}")  # Debug print
        self.path = path
        self._picture_added = False
        self._tags = {}  # Use a separate dictionary for tags
        self.picture_data = None  # Store picture data separately
        self.saved = False  # Add saved attribute

    def __setitem__(self, key, value):
        # print(f"FakeFLAC.__setitem__ called: {key} = {value}")  # Debug print
        self._tags[key] = value

    def __getitem__(self, key):
        # print(f"FakeFLAC.__getitem__ called for key: {key}")  # Debug print
        return self._tags[key]

    def get(self, key, default=None):  # Add get method for consistency
        # print(f"FakeFLAC.get called for key: {key}")  # Debug print
        return self._tags.get(key, default)

    def add_picture(self, pic) -> None:
        self.picture_data = pic.data  # simplified debug
        self._picture_added = True

    def save(self) -> None:
        # print("FakeFLAC.save called")  # Debug print
        self.saved = True


class FakePic:
    """Minimal representation of a FLAC picture."""

    def __init__(self):
        # print(f"FakePic.__init__ called")  # Debug print
        self.data: bytes | None = None
        self.type: int | None = None
        self.mime: str | None = None


@pytest.mark.asyncio
async def test_write_tags(monkeypatch, tmp_path: Path) -> None:
    """``write_tags`` should populate FLAC fields and embed art."""
    created: dict[str, FakeFLAC] = {}
    last_flac_instance = None

    def fake_flac(path: str) -> FakeFLAC:
        # print(f"fake_flac factory called with path: {path}")  # Debug print
        obj = FakeFLAC(path)
        created["obj"] = obj
        nonlocal last_flac_instance
        last_flac_instance = obj
        return obj

    def fake_picture() -> FakePic:
        # print(f"fake_picture factory called")  # Debug print
        return FakePic()

    monkeypatch.setattr(metadata, "FLAC", fake_flac)
    monkeypatch.setattr(metadata, "Picture", fake_picture)

    meta = TrackMetadata(
        title="S",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        year=2020,
        isrc="XYZ",
        lyrics="la",
        art_url="http://example.com/cover.jpg",
    )
    file_path = tmp_path / "x.flac"
    file_path.write_text("data")

    class DummyProvider(MetadataProviderPlugin):
        async def authenticate(self) -> None:
            pass

        async def open(self) -> None:  # pragma: no cover - unused
            pass

        async def close(self) -> None:  # pragma: no cover - unused
            pass

        async def search_track(self, query: str) -> object:
            return {}

        async def get_track(self, track_id: str) -> TrackMetadata:
            return meta

        async def get_album(self, album_id: str):  # pragma: no cover - unused
            return None

        async def fetch_cover_art(self, url: str) -> bytes:
            # print("DummyProvider.fetch_cover_art called")  # Debug print
            return b"img"

    class DummyLyrics(LyricsProviderPlugin):
        async def get_lyrics(self, artist: str, title: str) -> str:
            return "la"

        async def open(self) -> None:  # pragma: no cover - unused
            pass

        async def close(self) -> None:  # pragma: no cover - unused
            pass

    monkeypatch.setattr(
        DummyProvider, "fetch_cover_art", unittest.mock.AsyncMock(return_value=b"img")
    )

    new_path = await metadata.write_tags(
        file_path,
        meta,
        plugin=DummyProvider(),
        lyrics_plugin=DummyLyrics(),
        filename_template="{track_number}-{title}.flac",
    )

    flac = last_flac_instance
    assert flac is not None
    assert flac._picture_added is True
    assert flac.picture_data == b"img"
    assert flac.saved is True
    assert new_path.name == "01-S.flac"


@pytest.mark.asyncio
async def test_fetch_and_tag(monkeypatch, tmp_path: Path) -> None:
    """Lyrics should be fetched when missing and tags written."""
    captured: dict[str, object] = {}

    async def fake_get_lyrics(artist: str, title: str) -> str:
        # print(f"fake_get_lyrics called for {artist} - {title}")  # Debug print
        captured["lyrics"] = (artist, title)
        return "words"

    async def fake_write_tags(
        path: Path,
        meta: TrackMetadata,
        *,
        art: bytes | None = None,
        plugin: MetadataProviderPlugin | None = None,
        lyrics_plugin: LyricsProviderPlugin | None = None,
        filename_template: str | None = None,
    ) -> Path:
        if lyrics_plugin and not meta.lyrics:
            try:
                meta.lyrics = await lyrics_plugin.get_lyrics(
                    meta.artist,
                    meta.title,
                )
            except Exception:
                meta.lyrics = None

        captured["meta"] = meta
        captured["write"] = (
            path,
            captured["meta"],
            b"a",
            None,
        )
        return path

    monkeypatch.setattr(metadata, "write_tags", fake_write_tags)

    meta = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )
    path = tmp_path / "t.flac"
    path.write_text("d")

    class Plugin(LyricsProviderPlugin):
        async def get_lyrics(self, artist: str, title: str) -> str:
            # print(f"Plugin.get_lyrics called for {artist} - {title}")  # Debug print
            return await fake_get_lyrics(artist, title)

        async def open(self) -> None:  # pragma: no cover - unused
            pass

        async def close(self) -> None:  # pragma: no cover - unused
            pass

    await metadata.fetch_and_tag(path, meta, lyrics_plugin=Plugin(), art_data=b"a")

    assert captured["meta"].lyrics == "words"
    assert captured["write"] == (
        path,
        captured["meta"],
        b"a",
        None,
    )
    assert captured["lyrics"] == ("A", "T")


def test_cascade_merges() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )
    extra = TrackMetadata(
        title="",
        artist="",
        album="",
        track_number=1,
        disc_number=1,
        year=2024,
        lyrics="la",
    )

    merged = metadata.cascade(base, extra)
    assert merged.year == 2024
    assert merged.lyrics == "la"


def test_cascade_append_strategy() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        lyrics="first",
    )
    extra = TrackMetadata(
        title="",
        artist="",
        album="",
        track_number=1,
        disc_number=1,
        lyrics="second",
    )

    merged = metadata.cascade(base, extra, strategies={"lyrics": "append"})
    assert merged.lyrics == "firstsecond"


def test_cascade_replace_strategy() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )
    extra = TrackMetadata(
        title="T2",
        artist="B",
        album="C",
        track_number=2,
        disc_number=1,
    )

    merged = metadata.cascade(base, extra, strategies={"artist": "replace"})
    assert merged.artist == "B"
    assert merged.title == "T"


def test_cascade_prefer_strategy() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )
    extra = TrackMetadata(
        title="T2",
        artist="B",
        album="C",
        track_number=2,
        disc_number=1,
    )

    merged = metadata.cascade(base, extra, strategies={"title": "prefer"})
    assert merged.title == "T"


def test_generate_lrc() -> None:
    lyrics = "line1\nline2"
    text = metadata.generate_lrc(lyrics, step=10.0)
    assert text.startswith("[00:00.00]line1")
    assert "[00:10.00]line2" in text


def test_validate_field_retention_pass() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        isrc="123",
    )
    extra = TrackMetadata(
        title="T2",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        isrc="456",
    )
    merged = metadata.cascade(base, extra, strategies={"title": "prefer"})
    metadata.validate_field_retention(merged, [base, extra])


def test_validate_field_retention_error() -> None:
    base = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        isrc="123",
    )
    extra = TrackMetadata(
        title="",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        isrc=None,
    )
    merged = metadata.cascade(base, extra, strategies={"isrc": "replace"})
    merged.isrc = ""  # simulate bug where field was dropped
    with pytest.raises(ValueError):
        metadata.validate_field_retention(merged, [base, extra])


def test_merge_by_precedence() -> None:
    meta_a = TrackMetadata(
        title="A",
        artist="x",
        album="x",
        track_number=1,
        disc_number=1,
    )
    meta_b = TrackMetadata(
        title="B",
        artist="y",
        album="y",
        track_number=1,
        disc_number=1,
    )

    settings = Settings(plugin_precedence=["prov_b", "prov_a"])
    merged = metadata.merge_by_precedence(
        {"prov_a": meta_a, "prov_b": meta_b}, settings=settings
    )
    assert merged.title == "B"

    settings = Settings(plugin_precedence=["prov_a", "prov_b"])
    merged = metadata.merge_by_precedence(
        {"prov_a": meta_a, "prov_b": meta_b}, settings=settings
    )
    assert merged.title == "A"
