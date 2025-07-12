import os
from typing import Any
from unittest.mock import patch

import pytest

from flaccid.plugins import PLUGINS
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


@pytest.mark.asyncio
async def test_qobuz_env_token(monkeypatch):
    monkeypatch.setattr("keyring.get_password", lambda service, user: "ignored")
    with patch.dict(os.environ, {"QOBUZ_TOKEN": "envtok", "QOBUZ_APP_ID": "id"}):
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            assert plugin.token == "envtok"


@pytest.mark.asyncio
async def test_qobuz_refresh(monkeypatch):
    async def fake_refresh(self):
        self.token = "fresh"

    monkeypatch.setattr("keyring.get_password", lambda service, user: None)
    monkeypatch.setattr(QobuzPlugin, "_refresh_token", fake_refresh)
    with patch.dict(os.environ, {"QOBUZ_APP_ID": "id"}):
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            assert plugin.token == "fresh"


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
async def test_qobuz_metadata(monkeypatch):
    """Ensure album and track metadata are parsed."""

    track_data = {
        "title": "Song",
        "performer": {"name": "Artist"},
        "album": {
            "title": "Album",
            "release_date_original": "2024-01-01",
            "image": "cover.jpg",
        },
        "track_number": 1,
        "media_number": 1,
    }

    album_data = {
        "title": "Album",
        "artist": {"name": "Artist"},
        "release_date_original": "2024-01-01",
        "image": {"large": "cover.jpg"},
    }

    async def fake_request(self, endpoint: str, **params: Any):
        if endpoint == "track/get":
            return track_data
        return album_data

    monkeypatch.setattr(QobuzPlugin, "_request", fake_request)
    plugin = QobuzPlugin(app_id="id", token="t")
    async with plugin:
        track = await plugin.get_track("1")
        assert track.title == "Song"
        assert track.artist == "Artist"
        assert track.album == "Album"
        assert track.year == 2024
        album = await plugin.get_album("2")
        assert album.title == "Album"
        assert album.artist == "Artist"
        assert album.year == 2024
        assert album.cover_url == "cover.jpg"
