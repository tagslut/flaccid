from __future__ import annotations

"""Discogs API plugin for metadata lookup."""

import os
from typing import Any, Optional

import aiohttp
import keyring

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class DiscogsPlugin(MetadataProviderPlugin):
    """Basic Discogs API wrapper."""

    BASE_URL = "https://api.discogs.com/"

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or os.getenv("DISCOGS_TOKEN")
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        if not self.token:
            self.token = keyring.get_password("flaccid_discogs", "token")

    async def _request(self, endpoint: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        headers = {"Authorization": f"Discogs token={self.token}"}
        async with self.session.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        ) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("database/search", q=query, type="release")

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("database/search", q=query, type="release")

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request(f"tracks/{track_id}")
        return TrackMetadata(
            title=data.get("title", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            album=data.get("album", ""),
            track_number=int(data.get("position", 0)),
            disc_number=1,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request(f"releases/{album_id}")
        return AlbumMetadata(
            title=data.get("title", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            year=data.get("year"),
            cover_url=(data.get("images", [{}])[0].get("resource_url")),
        )
