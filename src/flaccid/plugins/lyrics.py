from __future__ import annotations

"""Simple lyrics provider using lyrics.ovh."""

from typing import Optional

import aiohttp

from .base import LyricsProviderPlugin


class LyricsPlugin(LyricsProviderPlugin):
    """Fetch lyrics for a track."""

    BASE_URL = "https://api.lyrics.ovh/v1/"

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        if not self.session:
            await self.open()
        assert self.session is not None
        async with self.session.get(f"{self.BASE_URL}{artist}/{title}") as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("lyrics")
