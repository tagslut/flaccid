
"""Unit tests for plugin discovery and registration."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from flaccid.plugins import PLUGINS
from flaccid.plugins.registry import get_provider
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.lyrics import LyricsPlugin
from flaccid.plugins.qobuz import QobuzPlugin
from flaccid.plugins.tidal import TidalPlugin
import keyring
from flaccid.core import downloader


@pytest.mark.asyncio
async def test_qobuz_plugin_auth(monkeypatch):
    def fake_get_password(service: str, user: str) -> str:
        return "user" if user == "username" else "pass"

    monkeypatch.setattr("keyring.get_password", fake_get_password)

    def fake_post(url, data=None):
        class Resp:
            async def json(self):
                return {"user_auth_token": "tok"}

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return Resp()

    with patch.dict(os.environ, {"QOBUZ_APP_ID": "id"}, clear=False):
        async with QobuzPlugin() as plugin:
            monkeypatch.setattr(plugin.session, "post", fake_post)
            await plugin.authenticate()
            assert plugin.token == "tok"


@pytest.mark.asyncio
async def test_qobuz_download(monkeypatch, tmp_path):
    async with QobuzPlugin(app_id="id", token="tok") as plugin:
        monkeypatch.setattr(
            plugin,
            "_request",
            AsyncMock(return_value={"url": "http://test"}),
        )
        monkeypatch.setattr(
            downloader,
            "download_file",
            AsyncMock(return_value=True),
        )
        result = await plugin.download("123", tmp_path / "file.flac")
        assert result is True


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


@pytest.mark.asyncio
async def test_tidal_auth_refresh(monkeypatch):
    """Authenticate using stored refresh token."""

    class FakeResp:
        async def json(self):
            return {"access_token": "new", "refresh_token": "next"}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class FakeSession:
        def __init__(self):
            self.post_called = False

        def post(self, url, data=None):
            self.post_called = True
            return FakeResp()

    plugin = TidalPlugin(token=None)
    plugin.session = FakeSession()

    monkeypatch.setattr(keyring, "get_password", lambda *a: "ref")
    saved: dict[str, str] = {}

    def save(service: str, user: str, token: str) -> None:  # pragma: no cover - simple
        saved["token"] = token

    monkeypatch.setattr(keyring, "set_password", save)

    await plugin.authenticate()
    assert plugin.token == "new"
    assert saved["token"] == "next"


@pytest.mark.asyncio
async def test_tidal_hls_download(tmp_path, monkeypatch):
    """Download an HLS playlist by concatenating segments."""

    playlist = "#EXTM3U\nseg1.ts\nseg2.ts"

    class FakeContent:
        def __init__(self, data: bytes) -> None:
            self.data = data

        async def iter_chunked(self, _size: int):
            yield self.data

    class FakeResp:
        def __init__(self, url: str) -> None:
            self.url = url
            self.status = 200
            self.content = FakeContent(b"a" if url.endswith("seg1.ts") else b"b")

        async def text(self):
            return playlist

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class FakeSession:
        def get(self, url: str):  # pragma: no cover - trivial
            return FakeResp(url)

    plugin = TidalPlugin(token="tok")
    plugin.session = FakeSession()
    monkeypatch.setattr(
        plugin,
        "_request",
        AsyncMock(return_value={"url": "http://x/playlist.m3u8"}),
    )

    dest = tmp_path / "out.flac"
    result = await plugin.download_track("1", dest)
    assert result is True
    assert dest.read_bytes() == b"ab"
