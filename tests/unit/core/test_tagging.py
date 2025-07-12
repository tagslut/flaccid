from __future__ import annotations

"""Tests for metadata tagging helpers."""

from pathlib import Path

import pytest

from flaccid.core import metadata
from flaccid.plugins.base import LyricsProviderPlugin, TrackMetadata


class FakeFLAC(dict):
    """Simple mock of :class:`mutagen.flac.FLAC`."""

    def add_picture(self, pic) -> None:  # pragma: no cover - simple stub
        self["pic"] = pic

    def save(self) -> None:  # pragma: no cover - simple stub
        self["saved"] = True


class FakePic:
    """Minimal representation of a FLAC picture."""

    def __init__(self) -> None:
        self.type: int | None = None
        self.mime: str | None = None
        self.data: bytes | None = None


def test_write_tags(monkeypatch, tmp_path: Path) -> None:
    """``write_tags`` should populate FLAC fields and embed art."""
    created: dict[str, FakeFLAC] = {}

    def fake_flac(path: str) -> FakeFLAC:
        obj = FakeFLAC()
        created["obj"] = obj
        return obj

    monkeypatch.setattr(metadata, "FLAC", fake_flac)
    monkeypatch.setattr(metadata, "Picture", FakePic)

    meta = TrackMetadata(
        title="S",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
        year=2020,
        isrc="XYZ",
        lyrics="la",
    )
    file_path = tmp_path / "x.flac"
    file_path.write_text("data")

    metadata.write_tags(file_path, meta, art=b"img")
    flac = created["obj"]
    assert isinstance(flac["pic"], FakePic)
    assert flac["pic"].data == b"img"
    assert flac.get("saved") is True


@pytest.mark.asyncio
async def test_fetch_and_tag(monkeypatch, tmp_path: Path) -> None:
    """Lyrics should be fetched when missing and tags written."""
    captured: dict[str, object] = {}

    async def fake_get_lyrics(artist: str, title: str) -> str:
        captured["lyrics"] = (artist, title)
        return "words"

    def fake_write(path: Path, meta: TrackMetadata, art: bytes | None = None) -> None:
        captured["write"] = (path, meta, art)

    monkeypatch.setattr(metadata, "write_tags", fake_write)

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
            return await fake_get_lyrics(artist, title)

        async def open(self) -> None:  # pragma: no cover - unused
            pass

        async def close(self) -> None:  # pragma: no cover - unused
            pass

    await metadata.fetch_and_tag(path, meta, lyrics_plugin=Plugin(), art_data=b"a")

    assert meta.lyrics == "words"
    assert captured["write"] == (path, meta, b"a")
    assert captured["lyrics"] == ("A", "T")
