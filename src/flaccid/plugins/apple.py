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
#!/usr/bin/env python3
"""
Apple Music plugin for the FLACCID CLI.

This module provides functionality for fetching metadata from Apple Music.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

from flaccid.plugins.base import BasePlugin, MetadataProviderPlugin, TrackMetadata


class AppleMusicPlugin(BasePlugin, MetadataProviderPlugin):
    """Plugin for fetching metadata from Apple Music."""

    BASE_URL = "https://api.music.apple.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Apple Music plugin.

        Args:
            api_key: Apple Music API key (defaults to APPLE_MUSIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("APPLE_MUSIC_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None

    async def open(self) -> None:
        """Initialize the HTTP session."""
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_track(self, track_id: str) -> TrackMetadata:
        """Get metadata for an Apple Music track.

        Args:
            track_id: Apple Music track ID

        Returns:
            Track metadata
        """
        if not self.session:
            await self.open()

        if not self.api_key:
            raise ValueError("Apple Music API key is required")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.BASE_URL}/catalog/us/songs/{track_id}"

        # In a real implementation, this would make an actual API request
        # For now, we'll just return dummy data
        # async with self.session.get(url, headers=headers) as response:
        #     data = await response.json()

        # This is dummy data to simulate a response
        # In a real implementation, we would parse the actual API response
        return TrackMetadata(
            title="Sample Track",
            artist="Sample Artist",
            album="Sample Album",
            track_number=1,
            disc_number=1,
            year=2025,
            isrc="USABC1234567",
            art_url="https://example.com/cover.jpg",
        )

    async def fetch_cover_art(self, url: str) -> Optional[bytes]:
        """Fetch cover art for a track.

        Args:
            url: URL of the cover art

        Returns:
            Cover art data or None if not available
        """
        if not self.session:
            await self.open()

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                return None
        except Exception:
            return None
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
