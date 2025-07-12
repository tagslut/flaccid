from __future__ import annotations

"""Asynchronous Tidal API client."""

import os
from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core import downloader

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class TidalPlugin(MetadataProviderPlugin):
    """Simplified Tidal API wrapper."""

    BASE_URL = "https://api.tidalhifi.com/v1/"

    def __init__(
        self,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.token = token or os.getenv("TIDAL_TOKEN")
        self.username = username or os.getenv("TIDAL_USERNAME")
        self.password = password or os.getenv("TIDAL_PASSWORD")
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def login(self) -> None:
        """Log in using ``username`` and ``password`` to obtain a token."""
        if not self.session:
            await self.open()
        data = await self._request(
            "login/username",
            method="post",
            username=self.username,
            password=self.password,
        )
        self.token = data.get("token")
        if self.token:
            keyring.set_password("flaccid_tidal", "token", self.token)

    async def authenticate(self) -> None:
        """Authenticate using stored token or login credentials."""
        if self.token:
            return
        self.token = keyring.get_password("flaccid_tidal", "token")
        if self.token:
            return
        # Attempt login if credentials are available
        if self.username and self.password:
            await self.login()

    async def _request(
        self, endpoint: str, method: str = "get", **params: Any
    ) -> Any:
        """Perform an HTTP request against the Tidal API."""
        assert self.session is not None, "Session not initialized"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        url = self.BASE_URL + endpoint
        if method.lower() == "post":
            async with self.session.post(url, json=params, headers=headers) as resp:
                return await resp.json()
        async with self.session.get(url, params=params, headers=headers) as resp:
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
        """Download a track to *dest*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        data = await self._request(f"tracks/{track_id}/streamUrl")
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None
        return await downloader.download_file(self.session, url, dest)
