import pytest
from unittest.mock import AsyncMock, patch

from flaccid.plugins.apple import AppleMusicPlugin


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_lookup_by_isrc(mock_get):
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json.return_value = {
        "results": [
            {
                "trackName": "Song",
                "artistName": "Artist",
                "collectionName": "Album",
                "trackNumber": 1,
                "discNumber": 1,
                "releaseDate": "2020-01-01T00:00:00Z",
                "isrc": "CODE",
                "artworkUrl100": "http://cover",
            }
        ]
    }
    mock_get.return_value.__aenter__.return_value = mock_resp

    async with AppleMusicPlugin() as plugin:
        track = await plugin.get_track(isrc="CODE")
        assert track.title == "Song"
        assert track.isrc == "CODE"

    async with AppleMusicPlugin() as plugin:
        track = await plugin.search_track(isrc="CODE")
        assert track.artist == "Artist"

    params = mock_get.call_args.kwargs["params"]
    assert params["isrc"] == "CODE"
    assert params["entity"] == "song"
