from __future__ import annotations

"""Asynchronous Apple Music API client."""

from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core.config import load_settings

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class AppleMusicPlugin(MetadataProviderPlugin):
    """Simplified Apple Music API wrapper."""

    ITUNES_URL = "https://itunes.apple.com/search"

    def __init__(self, developer_token: Optional[str] = None) -> None:
        settings = load_settings()
        self.developer_token = developer_token or settings.apple.developer_token
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        if not self.developer_token:
            token = keyring.get_password("flaccid_apple", "token")
            if token:
                self.developer_token = token

    async def _request(self, url: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request(self.ITUNES_URL, term=query, entity="song")

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request(self.ITUNES_URL, id=track_id, entity="song")
        track = data.get("results", [{}])[0]
        return TrackMetadata(
            title=track.get("trackName", ""),
            artist=track.get("artistName", ""),
            album=track.get("collectionName", ""),
            track_number=int(track.get("trackNumber", 0)),
            disc_number=int(track.get("discNumber", 0)),
            year=(
                int(track.get("releaseDate", "0")[:4])
                if track.get("releaseDate")
                else None
            ),
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request(self.ITUNES_URL, id=album_id, entity="album")
        album = data.get("results", [{}])[0]
        return AlbumMetadata(
            title=album.get("collectionName", ""),
            artist=album.get("artistName", ""),
            year=(
                int(album.get("releaseDate", "0")[:4])
                if album.get("releaseDate")
                else None
            ),
        )

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request(self.ITUNES_URL, term=query, entity="album")

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Downloading from Apple Music is not supported."""
        raise NotImplementedError("Apple Music does not provide downloads")
