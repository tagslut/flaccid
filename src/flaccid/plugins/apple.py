#!/usr/bin/env python3
"""Asynchronous Apple Music API client."""

from __future__ import annotations

import os
from typing import Any, Optional

import aiohttp

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class AppleMusicPlugin(MetadataProviderPlugin):
    """Simplified Apple Music API wrapper."""

    BASE_URL = "https://itunes.apple.com/search"

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the Apple Music plugin."""
        self.api_key = api_key or os.environ.get("APPLE_MUSIC_API_KEY")
        self.session: aiohttp.ClientSession | None = None

    async def authenticate(self) -> None:
        """Apple Music public API does not require authentication."""
        return None

    async def __aenter__(self) -> "AppleMusicPlugin":
        await self.open()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def _request(self, url: str, **params: Any) -> Any:
        assert self.session is not None, "Session not initialized"
        async with self.session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_track(
        self, track_id: str | None = None, *, isrc: str | None = None
    ) -> TrackMetadata:
        """Get metadata for an Apple Music track.

        If ``isrc`` is provided, lookup is performed using the ISRC code via the
        iTunes Search API.
        """
        if isrc:
            return await self.get_track_by_isrc(isrc)
        if not track_id:
            raise ValueError("track_id required if isrc not provided")

        data = await self._request(
            self.BASE_URL, id=track_id, entity="song", country="us"
        )
        if not data.get("results"):
            raise ValueError(f"Track with ID '{track_id}' not found.")

        track = data["results"][0]
        return TrackMetadata(
            title=track.get("trackName", ""),
            artist=track.get("artistName", ""),
            album=track.get("collectionName", ""),
            track_number=track.get("trackNumber"),
            disc_number=track.get("discNumber"),
            year=(
                int(track["releaseDate"][:4])
                if "releaseDate" in track and track["releaseDate"]
                else None
            ),
            isrc=track.get("isrc"),
            art_url=track.get("artworkUrl100"),
            source="apple",
        )

    async def get_track_by_isrc(self, isrc: str) -> TrackMetadata:
        """Lookup track metadata using the ISRC code."""
        data = await self._request(
            self.BASE_URL, isrc=isrc, entity="song", country="us"
        )
        if not data.get("results"):
            raise ValueError(f"Track with ISRC '{isrc}' not found.")

        track = data["results"][0]
        return TrackMetadata(
            title=track.get("trackName", ""),
            artist=track.get("artistName", ""),
            album=track.get("collectionName", ""),
            track_number=track.get("trackNumber"),
            disc_number=track.get("discNumber"),
            year=(
                int(track["releaseDate"][:4])
                if "releaseDate" in track and track["releaseDate"]
                else None
            ),
            isrc=track.get("isrc"),
            art_url=track.get("artworkUrl100"),
            source="apple",
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        """Get metadata for an Apple Music album using the iTunes Search API."""
        data = await self._request(
            self.BASE_URL, id=album_id, entity="album", country="us"
        )
        if not data.get("results"):
            raise ValueError(f"Album with ID '{album_id}' not found.")

        album = data["results"][0]
        return AlbumMetadata(
            title=album.get("collectionName", ""),
            artist=album.get("artistName", ""),
            year=(
                int(album["releaseDate"][:4])
                if "releaseDate" in album and album["releaseDate"]
                else None
            ),
        )

    async def search_track(
        self, query: str | None = None, *, isrc: str | None = None
    ) -> Any:
        """Search tracks by query or ISRC."""
        if isrc:
            return await self.get_track_by_isrc(isrc)
        if not query:
            raise ValueError("query required if isrc not provided")
        return await self._request(
            self.BASE_URL, term=query, entity="song", country="us"
        )

    async def fetch_cover_art(self, url: str) -> bytes | None:
        """Fetch cover art from a URL."""
        assert self.session, "Session not initialized"
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.read()
        except aiohttp.ClientError:
            return None

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        return await self._request(
            self.BASE_URL, term=query, entity="album", country="us"
        )
