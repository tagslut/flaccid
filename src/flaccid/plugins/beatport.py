from __future__ import annotations

"""Beatport API plugin."""

import os
from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core import downloader

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class BeatportPlugin(MetadataProviderPlugin):
    """Simplified Beatport API wrapper."""

    BASE_URL = "https://api.beatport.com/"

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or os.getenv("BEATPORT_TOKEN")
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        if not self.token:
            self.token = keyring.get_password("flaccid_beatport", "token")

    async def _request(self, endpoint: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with self.session.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        ) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search", query=query)

    async def search_album(self, query: str) -> Any:
        """Search Beatport releases."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search/releases", query=query)

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request(f"tracks/{track_id}")
        return TrackMetadata(
            title=data.get("name", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            album=data.get("release", {}).get("name", ""),
            track_number=int(data.get("number", 0)),
            disc_number=1,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request(f"releases/{album_id}")
        return AlbumMetadata(
            title=data.get("name", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            year=(
                data.get("releaseDate", "").split("-")[0]
                if data.get("releaseDate")
                else None
            ),
        )

    async def download_track(self, track_id: str, dest: Path) -> bool:
        await self.authenticate()
        if not self.session:
            await self.open()
        data = await self._request(f"tracks/{track_id}/download")
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None
        return await downloader.download_file(self.session, url, dest)
