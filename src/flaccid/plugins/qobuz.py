from __future__ import annotations

"""Asynchronous Qobuz API client."""

import os
from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core import downloader

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class QobuzPlugin(MetadataProviderPlugin):
    """Simple Qobuz API wrapper."""

    BASE_URL = "https://www.qobuz.com/api.json/0.2/"

    def __init__(
        self, app_id: Optional[str] = None, token: Optional[str] = None
    ) -> None:
        self.app_id = app_id or os.getenv("QOBUZ_APP_ID") or ""
        self.token = token or os.getenv("QOBUZ_TOKEN")
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        if not self.token:
            self.token = keyring.get_password("flaccid_qobuz", "token")
        # Real implementation would refresh token if needed

    async def _request(self, endpoint: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        params.setdefault("app_id", self.app_id)
        async with self.session.get(self.BASE_URL + endpoint, params=params) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search", query=query)

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request("track/get", track_id=track_id)
        return TrackMetadata(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            album=data.get("album", ""),
            track_number=int(data.get("track_number", 0)),
            disc_number=int(data.get("disc_number", 0)),
            year=data.get("year"),
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request("album/get", album_id=album_id)
        return AlbumMetadata(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            year=data.get("year"),
        )

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search", query=query, type="albums")

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Download a track to *dest*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        data = await self._request("track/getFileUrl", track_id=track_id, format_id=6)
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None
        return await downloader.download_file(self.session, url, dest)
