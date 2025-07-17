from __future__ import annotations

"""Discogs API plugin for metadata lookup."""

from typing import Any, Optional

import aiohttp
import keyring

from flaccid.core.config import load_settings
from flaccid.core.errors import AuthenticationError

from .base import AlbumMetadata, MetadataProviderPlugin, TrackMetadata


class DiscogsPlugin(MetadataProviderPlugin):
    """Basic Discogs API wrapper."""

    BASE_URL = "https://api.discogs.com/"

    def __init__(self, token: Optional[str] = None) -> None:
        settings = load_settings()
        self.token = token or settings.discogs_token
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
        """Load the Discogs token from keyring if not already set."""

        if not self.token:
            token = keyring.get_password("flaccid_discogs", "token")
            if token:
                self.token = token

        if not self.token:
            raise AuthenticationError(
                "Discogs token missing. Configure it via the 'fla set auth "
                "discogs' command."
            )

    async def _request(self, endpoint: str, **params: Any) -> Any:
        """Perform a GET request against the Discogs API."""

        assert self.session is not None, "Session not initialized"
        assert self.token, "Not authenticated"

        headers = {"Authorization": f"Discogs token={self.token}"}
        async with self.session.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        ) as resp:
            return await resp.json()

    async def search_track(self, query: str) -> Any:
        """Search Discogs for ``query`` and return raw results."""

        await self.authenticate()
        if not self.session:
            await self.open()
        return await self._request("database/search", q=query, type="release")

    async def get_track(self, track_id: str) -> TrackMetadata:
        """Retrieve track metadata by Discogs ``track_id``."""

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
        """Retrieve album metadata by Discogs ``album_id``."""

        await self.authenticate()
        data = await self._request(f"releases/{album_id}")
        return AlbumMetadata(
            title=data.get("title", ""),
            artist=data.get("artists", [{}])[0].get("name", ""),
            year=data.get("year"),
            cover_url=(data.get("images", [{}])[0].get("resource_url")),
        )
