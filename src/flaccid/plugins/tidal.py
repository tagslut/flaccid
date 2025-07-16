from __future__ import annotations

"""Asynchronous Tidal API client (placeholder)."""

from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin
import contextlib

import aiohttp
import keyring
from flaccid.core.config import load_settings

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class TidalPlugin(MetadataProviderPlugin):
    """Simplified Tidal API wrapper."""

    BASE_URL = "https://api.tidalhifi.com/v1/"
    AUTH_URL = "https://auth.tidal.com/v1/oauth2/token"

    token: str | None

    def __init__(self, token: Optional[str] = None) -> None:
        """Create a new plugin instance."""
        settings = load_settings()
        # Allow caller-supplied token or fallback to configuration.
        self.token = token or settings.tidal_token or None
        self.session: Optional[aiohttp.ClientSession] = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        """Authenticate using a stored refresh token."""
        if self.token:
            return

        refresh_token = keyring.get_password("flaccid_tidal", "refresh_token")
        if not refresh_token:
            raise RuntimeError(
                "Tidal refresh token missing. Run 'fla set auth tidal' first."
            )

        assert self.session is not None, "Session not initialized"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        async with self.session.post(self.AUTH_URL, data=payload) as resp:
            data = await resp.json()

        access_token = data.get("access_token")
        if not access_token:
            raise RuntimeError("Failed to authenticate with Tidal")

        self.token = access_token
        new_refresh = data.get("refresh_token")
        if new_refresh:
            try:
                keyring.set_password("flaccid_tidal", "refresh_token", new_refresh)
            except Exception:
                pass

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
        year: int | None = None
        date_str = data.get("streamStartDate")
        if isinstance(date_str, str) and date_str:
            with contextlib.suppress(ValueError):
                year = int(date_str.split("-")[0])

        album_info = data.get("album", {})
        if isinstance(album_info, dict):
            album_title = album_info.get("title", "")
            art_url = album_info.get("cover")
            artist = album_info.get("artist", data.get("artist"))
        else:
            album_title = data.get("album", "")
            art_url = None
            artist = data.get("artist")

        artist_name = artist.get("name") if isinstance(artist, dict) else artist or ""

        return TrackMetadata(
            title=data.get("title", ""),
            artist=artist_name,
            album=album_title,
            track_number=int(data.get("trackNumber", 0)),
            disc_number=int(data.get("volumeNumber", 0)),
            year=year,
            isrc=data.get("isrc"),
            art_url=art_url,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        await self.authenticate()
        data = await self._request(f"albums/{album_id}")
        year: int | None = None
        date_str = data.get("releaseDate")
        if isinstance(date_str, str) and date_str:
            with contextlib.suppress(ValueError):
                year = int(date_str.split("-")[0])

        artist = data.get("artist")
        artist_name = artist.get("name") if isinstance(artist, dict) else artist or ""

        return AlbumMetadata(
            title=data.get("title", ""),
            artist=artist_name,
            year=year,
            cover_url=data.get("cover"),
        )

    async def search_album(self, query: str) -> Any:
        """Search albums by *query*."""
        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search/albums", query=query)

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Download a track to ``dest`` using the HLS stream."""
        await self.authenticate()
        if not self.session:
            await self.open()
        data = await self._request(f"tracks/{track_id}/streamUrl")
        url = data.get("url")
        if not url:
            return False
        assert self.session is not None

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return False
            playlist = await resp.text()

        base = url.rsplit("/", 1)[0] + "/"
        segment_urls = [
            urljoin(base, line)
            for line in playlist.splitlines()
            if line and not line.startswith("#")
        ]

        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fh:
            for seg_url in segment_urls:
                async with self.session.get(seg_url) as seg_resp:
                    if seg_resp.status != 200:
                        return False
                    async for chunk in seg_resp.content.iter_chunked(1024):
                        fh.write(chunk)

        return True
