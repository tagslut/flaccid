"""Unit tests for plugin discovery and registration."""

import os
from unittest.mock import patch

import pytest

from flaccid.plugins import PLUGINS
from flaccid.plugins.registry import get_provider
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.lyrics import LyricsPlugin
from flaccid.plugins.qobuz import QobuzPlugin


@pytest.mark.asyncio
async def test_qobuz_plugin_auth(monkeypatch):
    monkeypatch.setattr("keyring.get_password", lambda service, user: "secret")
    with patch.dict(os.environ, {"QOBUZ_APP_ID": "id"}, clear=False):
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            assert plugin.token == "secret"


def test_track_metadata_dataclass():
    meta = TrackMetadata(
        title="Song",
        artist="Artist",
        album="Album",
        track_number=1,
        disc_number=1,
        year=2020,
    )
    assert meta.title == "Song"
    assert meta.year == 2020


def test_plugin_registry_contains_new_plugins():
    assert "discogs" in PLUGINS
    assert "beatport" in PLUGINS
    assert "lyrics" in PLUGINS


def test_get_provider_returns_plugin():
    assert get_provider("qobuz") is QobuzPlugin
    with pytest.raises(ValueError):
        get_provider("unknown")


@pytest.mark.asyncio
async def test_lyrics_plugin(tmp_path, monkeypatch):
    """Ensure LyricsPlugin returns lyrics on success."""

    def fake_get(url, **kwargs):
        class Resp:
            status = 200

            async def json(self):
                return {"lyrics": "la la"}

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return Resp()

    plugin = LyricsPlugin()
    async with plugin:
        monkeypatch.setattr(plugin.session, "get", fake_get)
        lyrics = await plugin.get_lyrics("artist", "song")
        assert lyrics == "la la"


@pytest.mark.asyncio
async def test_lyrics_plugin_handles_errors(monkeypatch):
    """Plugin should return ``None`` on request failure."""

    def fake_get(url, **kwargs):
        class Resp:
            status = 404

            async def json(self):  # pragma: no cover - not used
                return {}

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return Resp()

    plugin = LyricsPlugin()
    async with plugin:
        monkeypatch.setattr(plugin.session, "get", fake_get)
        lyrics = await plugin.get_lyrics("artist", "song")
        assert lyrics is None

