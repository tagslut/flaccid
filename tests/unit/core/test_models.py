from __future__ import annotations

# ruff: noqa: E402

"""Unit tests for dataclasses and base plugin behavior."""

import pytest

import importlib.util
import sys
import types
from pathlib import Path

path = Path(__file__).resolve().parents[3] / "src" / "flaccid" / "plugins" / "base.py"
sys.modules.setdefault("flaccid", types.ModuleType("flaccid"))
sys.modules.setdefault("flaccid.plugins", types.ModuleType("flaccid.plugins"))
spec = importlib.util.spec_from_file_location(
    "flaccid.plugins.base", path, submodule_search_locations=[str(path.parent)]
)
base = importlib.util.module_from_spec(spec)
sys.modules["flaccid.plugins.base"] = base
assert spec.loader is not None
spec.loader.exec_module(base)

AlbumMetadata = base.AlbumMetadata
LyricsProviderPlugin = base.LyricsProviderPlugin
MetadataProviderPlugin = base.MetadataProviderPlugin
MusicServicePlugin = base.MusicServicePlugin
TrackMetadata = base.TrackMetadata


def test_track_metadata_defaults() -> None:
    """Ensure optional fields of :class:`TrackMetadata` default to ``None``."""
    meta = TrackMetadata(
        title="Song",
        artist="Artist",
        album="Album",
        track_number=1,
        disc_number=1,
    )
    assert meta.year is None
    assert meta.isrc is None
    assert meta.lyrics is None


def test_album_metadata_fields() -> None:
    """Verify :class:`AlbumMetadata` stores provided values."""
    album = AlbumMetadata(title="A", artist="B", year=2024, cover_url="u")
    assert album.title == "A"
    assert album.artist == "B"
    assert album.year == 2024
    assert album.cover_url == "u"


class DummyPlugin(MusicServicePlugin):
    """Concrete plugin for testing context manager methods."""

    opened: bool = False
    closed: bool = False

    async def open(self) -> None:  # pragma: no cover - trivial
        self.opened = True

    async def close(self) -> None:  # pragma: no cover - trivial
        self.closed = True


@pytest.mark.asyncio
async def test_music_service_plugin_context_manager() -> None:
    """The base class should invoke ``open`` and ``close``."""
    plugin = DummyPlugin()
    async with plugin as ctx:
        assert ctx.opened is True
    assert plugin.closed is True


def test_base_classes_are_abstract() -> None:
    """Instantiate base plugin classes should raise :class:`TypeError`."""
    with pytest.raises(TypeError):
        MusicServicePlugin()
    with pytest.raises(TypeError):
        MetadataProviderPlugin()
    with pytest.raises(TypeError):
        LyricsProviderPlugin()
