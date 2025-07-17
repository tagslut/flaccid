from __future__ import annotations

"""Beatport API plugin."""

from pathlib import Path
from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core import downloader
from flaccid.core.config import load_settings
from flaccid.core.errors import AuthenticationError

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class BeatportPlugin(MetadataProviderPlugin):
    """Simplified Beatport API wrapper."""

    BASE_URL = "https://api.beatport.com/"

    def __init__(self, token: Optional[str] = None) -> None:
        settings = load_settings()
        # Must be a concrete str to satisfy the base-class type
        self.token: str = token or settings.beatport_token or ""
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        """Create the underlying :class:`aiohttp.ClientSession`."""

        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the HTTP session."""

        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> None:
        """Load the Beatport token from keyring if not already set."""

        if not self.token:
            keyring_token = keyring.get_password("flaccid_beatport", "token")
            if keyring_token:
                self.token = keyring_token

        if not self.token:
            raise AuthenticationError(
                "Beatport token missing. Configure it via the 'fla set auth "
                "beatport' command."
            )

    async def _request(self, endpoint: str, **params: Any) -> Any:
        """Perform a GET request against the Beatport API."""

        assert self.session is not None, "Session not initialized"
        assert self.token, "Not authenticated"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with self.session.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        ) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        """Search Beatport for ``query`` and return raw results."""

        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("search", query=query)

    async def get_track(self, track_id: str) -> TrackMetadata:
        """Retrieve track metadata by Beatport ``track_id``."""

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
        """Retrieve album metadata by Beatport ``album_id``."""

        await self.authenticate()
        data = await self._request(f"releases/{album_id}")
        return AlbumMetadata(
            title=data.get("name", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            year=(
                data.get("release_date", "").split("-")[0]
                if data.get("release_date")
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
