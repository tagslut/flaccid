from __future__ import annotations

# ruff: noqa: E402

"""Lyrics provider using the Musixmatch API."""

import os
from typing import Optional

import aiohttp

from .base import LyricsProviderPlugin


class MusixmatchPlugin(LyricsProviderPlugin):
    """Fetch lyrics using the Musixmatch API."""

    BASE_URL = "https://api.musixmatch.com/ws/1.1"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("MUSIXMATCH_API_KEY")
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
        if not self.api_key:
            return None
        if not self.session:
            await self.open()
        assert self.session is not None
        params = {
            "q_track": title,
            "q_artist": artist,
            "apikey": self.api_key,
        }
        try:
            async with self.session.get(
                f"{self.BASE_URL}/matcher.lyrics.get", params=params
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
            lyrics = (
                data.get("message", {})
                .get("body", {})
                .get("lyrics", {})
                .get("lyrics_body")
            )
            if isinstance(lyrics, str):
                return lyrics.strip()
        except aiohttp.ClientError:
            return None
        return None
