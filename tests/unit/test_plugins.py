"""Unit tests for plugin discovery and registration."""

import os
from unittest.mock import AsyncMock, patch
import aiohttp
import asyncio

import pytest

from flaccid.plugins import PLUGINS
from flaccid.plugins.registry import get_provider
from flaccid.plugins.loader import PluginLoader
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.lyrics import LyricsPlugin, LyricsOvhProvider
from flaccid.plugins.qobuz import QobuzPlugin
from flaccid.plugins.tidal import TidalPlugin
from flaccid.plugins.discogs import DiscogsPlugin
from flaccid.plugins.beatport import BeatportPlugin
from flaccid.plugins.base import LyricsProviderPlugin
from flaccid.core.errors import AuthenticationError
from typing import Optional
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
async def test_qobuz_plugin_auth_missing(monkeypatch):
    """Authentication should fail when credentials are absent."""
    monkeypatch.setattr("keyring.get_password", lambda *a: None)
    plugin = QobuzPlugin(app_id="id", token=None)
    plugin.session = aiohttp.ClientSession()
    with pytest.raises(AuthenticationError):
        await plugin.authenticate()
    await plugin.session.close()


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


def test_plugin_loader_discovers_plugins(tmp_path):
    module = tmp_path / "dummy.py"
    module.write_text(
        """
from flaccid.plugins.base import MetadataProviderPlugin, TrackMetadata, AlbumMetadata

class DummyPlugin(MetadataProviderPlugin):
    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def authenticate(self) -> None:
        pass

    async def search_track(self, query: str):
        return {}

    async def get_track(self, track_id: str) -> TrackMetadata:
        return TrackMetadata(
            title="t",
            artist="a",
            album="b",
            track_number=1,
            disc_number=1,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        return AlbumMetadata(title="t", artist="a")
"""
    )

    loader = PluginLoader(tmp_path)
    plugins = loader.discover()
    assert "dummy" in plugins
    assert plugins["dummy"].__name__ == "DummyPlugin"


def test_get_provider_returns_plugin():
    assert get_provider("qobuz") is QobuzPlugin
    with pytest.raises(ValueError):
        get_provider("unknown")


@pytest.mark.asyncio
async def test_lyrics_plugin(tmp_path, monkeypatch):
    """Ensure LyricsPlugin returns lyrics on success."""

    def fake_get(url, **_kwargs):
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
        provider = plugin.providers[0]
        assert isinstance(provider, LyricsOvhProvider)
        monkeypatch.setattr(provider.session, "get", fake_get)
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
        provider = plugin.providers[0]
        assert isinstance(provider, LyricsOvhProvider)
        monkeypatch.setattr(provider.session, "get", fake_get)
        lyrics = await plugin.get_lyrics("artist", "song")
        assert lyrics is None


@pytest.mark.asyncio
async def test_lyrics_plugin_fallback_and_cache():
    """LyricsPlugin should try providers in order and cache results."""

    class Dummy(LyricsProviderPlugin):
        def __init__(self, result: Optional[str]) -> None:
            self.result = result
            self.calls = 0

        async def open(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
            self.calls += 1
            return self.result

    p1 = Dummy(None)
    p2 = Dummy("found")
    plugin = LyricsPlugin()
    plugin.providers = [p1, p2]

    lyr1 = await plugin.get_lyrics("a", "b")
    lyr2 = await plugin.get_lyrics("a", "b")

    assert lyr1 == "found"
    assert lyr2 == "found"  # cached
    assert p1.calls == 1
    assert p2.calls == 1


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
async def test_tidal_auth_login(monkeypatch):
    """Authenticate using username/password when no refresh token exists."""

    class FakeResp:
        async def json(self):
            return {"access_token": "tok", "refresh_token": "newref"}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class FakeSession:
        def post(self, url, data=None):  # pragma: no cover - trivial
            assert data["grant_type"] == "password"
            assert data["username"] == "user"
            assert data["password"] == "pass"
            return FakeResp()

    plugin = TidalPlugin(token=None)
    plugin.session = FakeSession()

    def get_password(service: str, user: str) -> str | None:
        mapping = {"username": "user", "password": "pass"}
        return mapping.get(user)

    monkeypatch.setattr(keyring, "get_password", get_password)
    saved: dict[str, str] = {}

    def save(service: str, user: str, token: str) -> None:  # pragma: no cover - simple
        saved[user] = token

    monkeypatch.setattr(keyring, "set_password", save)

    await plugin.authenticate()
    assert plugin.token == "tok"
    assert saved["refresh_token"] == "newref"


@pytest.mark.asyncio
async def test_tidal_auth_missing(monkeypatch):
    """Raise AuthenticationError when no credentials are stored."""
    plugin = TidalPlugin(token=None)
    plugin.session = aiohttp.ClientSession()
    monkeypatch.setattr(keyring, "get_password", lambda *a: None)
    with pytest.raises(AuthenticationError):
        await plugin.authenticate()
    await plugin.session.close()


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


@pytest.mark.asyncio
async def test_tidal_hls_segment_retry(tmp_path, monkeypatch):
    """Segments should be retried when a 429 status is received."""

    playlist = "#EXTM3U\nseg1.ts\nseg2.ts"

    class FakeContent:
        def __init__(self, data: bytes) -> None:
            self.data = data

        async def iter_chunked(self, _size: int):
            yield self.data

    class Resp:
        def __init__(self, url: str, status: int = 200) -> None:
            self.url = url
            self.status = status
            self.content = FakeContent(b"a" if url.endswith("seg1.ts") else b"b")
            self._headers: dict[str, str] = {}

        async def text(self):
            return playlist

        def raise_for_status(self) -> None:
            if self.status >= 400 and self.status != 429:
                raise aiohttp.ClientResponseError(None, None, status=self.status)

        @property
        def headers(self) -> dict[str, str]:
            return self._headers

        async def release(self) -> None:  # pragma: no cover - trivial
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    calls: list[int] = []

    class Session:
        async def get(self, url: str):
            if "playlist.m3u8" in url:
                return Resp(url)
            if url.endswith("seg1.ts") and not calls:
                resp = Resp(url, 429)
                resp._headers = {"Retry-After": "0"}
                calls.append(429)
                return resp
            calls.append(200)
            return Resp(url)

    plugin = TidalPlugin(token="tok")
    plugin.session = Session()
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(
        plugin,
        "_request",
        AsyncMock(return_value={"url": "http://x/playlist.m3u8"}),
    )

    dest = tmp_path / "seg.flac"
    result = await plugin.download_track("1", dest)
    assert result is True
    assert dest.read_bytes() == b"ab"
    assert calls == [429, 200]


@pytest.mark.asyncio
async def test_tidal_request_retry(monkeypatch):
    """_request should retry on HTTP 429 responses."""

    class Resp:
        def __init__(self, status: int) -> None:
            self.status = status

        async def json(self):
            return {"ok": True}

        def raise_for_status(self) -> None:
            if self.status >= 400:
                raise aiohttp.ClientResponseError(None, None, status=self.status)

        @property
        def headers(self) -> dict[str, str]:
            return {"Retry-After": "0"} if self.status == 429 else {}

        async def release(self) -> None:  # pragma: no cover - trivial
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    calls = []

    class Session:
        async def get(self, *_args, **_kwargs):
            status = 429 if len(calls) == 0 else 200
            calls.append(status)
            return Resp(status)

    plugin = TidalPlugin(token="tok")
    plugin.session = Session()
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    result = await plugin._request("test")
    assert result == {"ok": True}
    assert calls == [429, 200]


@pytest.mark.asyncio
async def test_tidal_browse_album(monkeypatch):
    plugin = TidalPlugin(token="tok")
    tracks = [
        {
            "item": {
                "id": "1",
                "title": "Song",
                "artist": {"name": "Artist"},
                "album": "A",
            }
        }
    ]
    monkeypatch.setattr(plugin, "_request", AsyncMock(return_value={"items": tracks}))
    result = await plugin.browse_album("1")
    assert result[0].title == "Song"


@pytest.mark.asyncio
async def test_tidal_download_playlist(tmp_path, monkeypatch):
    plugin = TidalPlugin(token="tok")
    monkeypatch.setattr(plugin, "download_track", AsyncMock(return_value=True))
    monkeypatch.setattr(
        plugin,
        "_request",
        AsyncMock(
            return_value={"items": [{"item": {"id": "1"}}, {"item": {"id": "2"}}]}
        ),
    )
    dests = await plugin.download_playlist("p", tmp_path)
    assert len(dests) == 2


@pytest.mark.asyncio
async def test_discogs_auth(monkeypatch):
    monkeypatch.setattr(keyring, "get_password", lambda *a: "tok")

    plugin = DiscogsPlugin(token=None)
    await plugin.authenticate()
    assert plugin.token == "tok"


@pytest.mark.asyncio
async def test_discogs_auth_missing(monkeypatch):
    monkeypatch.setattr(keyring, "get_password", lambda *a: None)
    plugin = DiscogsPlugin(token=None)
    with pytest.raises(AuthenticationError):
        await plugin.authenticate()


@pytest.mark.asyncio
async def test_discogs_get_track(monkeypatch):
    async with DiscogsPlugin(token="tok") as plugin:
        monkeypatch.setattr(
            plugin,
            "_request",
            AsyncMock(
                return_value={
                    "title": "Song",
                    "artists": [{"name": "Artist"}],
                    "album": "Album",
                    "position": "1",
                }
            ),
        )
        track = await plugin.get_track("123")
        assert track.title == "Song"
        assert track.artist == "Artist"


@pytest.mark.asyncio
async def test_beatport_auth(monkeypatch):
    monkeypatch.setattr(keyring, "get_password", lambda *a: "tok")

    plugin = BeatportPlugin(token="")
    await plugin.authenticate()
    assert plugin.token == "tok"


@pytest.mark.asyncio
async def test_beatport_auth_missing(monkeypatch):
    monkeypatch.setattr(keyring, "get_password", lambda *a: None)
    plugin = BeatportPlugin(token="")
    with pytest.raises(AuthenticationError):
        await plugin.authenticate()


@pytest.mark.asyncio
async def test_beatport_get_track(monkeypatch):
    async with BeatportPlugin(token="tok") as plugin:
        monkeypatch.setattr(
            plugin,
            "_request",
            AsyncMock(
                return_value={
                    "name": "Song",
                    "artists": [{"name": "Artist"}],
                    "release": {"name": "Album"},
                    "number": 2,
                }
            ),
        )
        track = await plugin.get_track("1")
        assert track.album == "Album"
