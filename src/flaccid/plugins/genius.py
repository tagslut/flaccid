from __future__ import annotations

# ruff: noqa: E402

"""Lyrics provider using the Genius API."""

import os
from typing import Optional

import aiohttp

from .base import LyricsProviderPlugin


class GeniusPlugin(LyricsProviderPlugin):
    """Fetch lyrics using the Genius API."""

    BASE_URL = "https://api.genius.com"

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or os.getenv("GENIUS_TOKEN")
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        """Create the underlying :class:`aiohttp.ClientSession`."""
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Return lyrics for *artist* and *title* or ``None`` if not found."""
        if not self.token:
            return None
        if not self.session:
            await self.open()
        assert self.session is not None
        headers = {"Authorization": f"Bearer {self.token}"}
        query = f"{artist} {title}"
        try:
            async with self.session.get(
                f"{self.BASE_URL}/search", params={"q": query}, headers=headers
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
            hits = data.get("response", {}).get("hits", [])
            if not hits:
                return None
            song_id = hits[0].get("result", {}).get("id")
            if not song_id:
                return None
            async with self.session.get(
                f"{self.BASE_URL}/songs/{song_id}", headers=headers
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
            lyrics = data.get("response", {}).get("song", {}).get("lyrics")
            return lyrics.strip() if isinstance(lyrics, str) else None
        except aiohttp.ClientError:
            return None
