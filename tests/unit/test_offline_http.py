"""Offline HTTP tests using aiohttp mocks."""


import pytest
from aioresponses import aioresponses

from flaccid.plugins.lyrics import LyricsOvhProvider
from flaccid.plugins.tidal import TidalPlugin


@pytest.mark.asyncio
async def test_lyrics_provider_offline(monkeypatch, lyrics_ovh_response, tmp_path):
    """Lyrics provider should return lyrics using mocked HTTP."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    provider = LyricsOvhProvider()
    async with provider:
        with aioresponses() as mocked:
            url = provider.BASE_URL + "Artist/Title"
            mocked.get(url, payload=lyrics_ovh_response, status=200)
            lyrics = await provider.get_lyrics("Artist", "Title")
    assert lyrics == lyrics_ovh_response["lyrics"]


@pytest.mark.asyncio
async def test_tidal_get_track_offline(monkeypatch, tidal_track_response, tmp_path):
    """TidalPlugin.get_track should parse JSON from a mocked request."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    plugin = TidalPlugin(token="tok")
    async with plugin:
        with aioresponses() as mocked:
            url = plugin.BASE_URL + "tracks/123"
            mocked.get(url, payload=tidal_track_response, status=200)
            track = await plugin.get_track("123")
    assert track.title == "My Song"
    assert track.artist == "My Artist"
    assert track.album == "My Album"
    assert track.track_number == 1
    assert track.disc_number == 1
    assert track.year == 2021
