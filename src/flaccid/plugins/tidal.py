from __future__ import annotations

"""Asynchronous Tidal API client (placeholder)."""

from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core import downloader
from flaccid.core.config import load_settings

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class TidalPlugin(MetadataProviderPlugin):
    """Simplified Tidal API wrapper."""

    BASE_URL = "https://api.tidalhifi.com/v1/"
    token: str

    def __init__(self, token: Optional[str] = None) -> None:
        settings = load_settings()
        # Allow caller-supplied token or fallback to configuration
        self.token = token or settings.tidal_token or ""
        assert self.token, "TIDAL_API_TOKEN is required"
        self.session: Optional[aiohttp.ClientSession] = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        if not self.token:
            keyring_token = keyring.get_password("flaccid_tidal", "token")
            if keyring_token:
                self.token = keyring_token

    async def _request(self, endpoint: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        # mypy: after this assert self.token is str
        assert self.token is not None, "Not authenticated"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with self.session.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        ) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search/tracks", query=query)

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request(f"tracks/{track_id}")
        return TrackMetadata(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            album=data.get("album", ""),
            track_number=int(data.get("trackNumber", 0)),
            disc_number=int(data.get("volumeNumber", 0)),
            year=(
                data.get("streamStartDate", "").split("-")[0]
                if data.get("streamStartDate")
                else None
            ),
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request(f"albums/{album_id}")
        return AlbumMetadata(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            year=(
                data.get("releaseDate", "").split("-")[0]
                if data.get("releaseDate")
                else None
            ),
        )

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search/albums", query=query)

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Download a track to *dest* (placeholder)."""
        await self.authenticate()
        if not self.session:
            await self.open()
        data = await self._request(f"tracks/{track_id}/streamUrl")
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None
        return await downloader.download_file(self.session, url, dest)
