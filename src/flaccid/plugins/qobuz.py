#!/usr/bin/env python3
"""
Qobuz plugin for the FLACCID CLI.

This module provides functionality for downloading tracks from Qobuz.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp
import keyring

from flaccid.core import downloader
from flaccid.core.config import load_settings
from flaccid.plugins.base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class QobuzPlugin(MetadataProviderPlugin):
    """Simple Qobuz API wrapper."""

    BASE_URL = "https://www.qobuz.com/api.json/0.2/"

    def __init__(
        self, app_id: Optional[str] = None, token: Optional[str] = None
    ) -> None:
        settings = load_settings()
        self.app_id = app_id or settings.qobuz.app_id
        self.token = token or settings.qobuz.token
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "QobuzPlugin":
        """Enter the async context manager."""
        await self.open()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit the async context manager."""
        await self.close()

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> bool:
        """Ensure a valid authentication token is available."""
        if not self.token:
            self.token = keyring.get_password("flaccid_qobuz", "token")
            if self.token is None:
                raise RuntimeError(
                    "Qobuz token not found in keyring. Please set your token."
                )
            await self._refresh_token()
        return True

    async def _refresh_token(self) -> None:
        """Refresh the stored authentication token."""
        assert self.session is not None, "Session not initialized"
        async with self.session.get(
            self.BASE_URL + "login/refresh",
            params={"app_id": self.app_id, "user_auth_token": self.token},
        ) as resp:
            data = await resp.json()
        token = data.get("user_auth_token")
        if not token:
            raise RuntimeError("Failed to refresh Qobuz token")
        self.token = token
        try:
            keyring.set_password("flaccid_qobuz", "token", token)
        except Exception:
            pass

    async def _request(self, endpoint: str, **params: Any) -> Any:
        """Perform an API request and refresh the token on 401 responses."""
        assert self.session is not None, "Session not initialized"
        params.setdefault("app_id", self.app_id)
        if self.token:
            params.setdefault("user_auth_token", self.token)
        resp = await self.session.get(self.BASE_URL + endpoint, params=params)
        if resp.status == 401:
            await self._refresh_token()
            params["user_auth_token"] = self.token
            resp = await self.session.get(self.BASE_URL + endpoint, params=params)

        resp.raise_for_status()
        return await resp.json()

    async def search_track(self, query: str) -> Any:
        await self.authenticate()
        return await self._request("search", query=query)

    async def get_track(self, track_id: str) -> TrackMetadata:
        await self.authenticate()
        data = await self._request("track/get", track_id=track_id)

        album_info = data.get("album", {})
        year = None
        date_str = album_info.get("release_date_original") or data.get("year")
        if isinstance(date_str, str) and date_str:
            with contextlib.suppress(ValueError):
                year = int(date_str.split("-")[0])

        image = album_info.get("image")
        art_url = None
        if isinstance(image, dict):
            art_url = image.get("large") or image.get("small")
        elif isinstance(image, str):
            art_url = image

        return TrackMetadata(
            title=data.get("title", ""),
            artist=data.get("performer", {}).get("name") or data.get("artist", ""),
            album=album_info.get("title", data.get("album", "")),
            track_number=int(data.get("track_number", data.get("trackNumber", 0))),
            disc_number=int(data.get("disc_number", data.get("media_number", 0))),
            year=year,
            isrc=data.get("isrc"),
            art_url=art_url,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request("album/get", album_id=album_id)

        year = None
        date_str = data.get("release_date_original") or data.get("year")
        if isinstance(date_str, str) and date_str:
            with contextlib.suppress(ValueError):
                year = int(date_str.split("-")[0])

        artist = data.get("artist")
        if isinstance(artist, dict):
            artist = artist.get("name", "")

        image = data.get("image")
        if isinstance(image, dict):
            cover_url = image.get("large") or image.get("small")
        else:
            cover_url = image

        return AlbumMetadata(
            title=data.get("title", ""),
            artist=artist or "",
            year=year,
            cover_url=cover_url,
        )

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        return await self._request("search", query=query, type="albums")

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Download a track to *dest*."""
        await self.authenticate()
        data = await self._request("track/getFileUrl", track_id=track_id, format_id=6)
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None
        return await downloader.download_file(self.session, url, dest)
