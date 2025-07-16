from __future__ import annotations

# ruff: noqa: E402

"""Lyrics provider implementations."""

from collections import OrderedDict
from typing import Optional

import aiohttp

from .base import LyricsProviderPlugin


class LyricsOvhProvider(LyricsProviderPlugin):
    """Fetch lyrics for a track using lyrics.ovh."""

    BASE_URL = "https://api.lyrics.ovh/v1/"

    def __init__(self) -> None:
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

        if not self.session:
            await self.open()
        assert self.session is not None

        url = f"{self.BASE_URL}{artist}/{title}"
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        except aiohttp.ClientError:
            return None

        lyrics = data.get("lyrics")
        return lyrics.strip() if isinstance(lyrics, str) else None


class _LRUCache:
    """Simple LRU cache for lyrics queries."""

    def __init__(self, maxsize: int) -> None:
        self.maxsize = maxsize
        self._data: OrderedDict[str, Optional[str]] = OrderedDict()

    def get(self, key: str) -> Optional[str] | None:
        if key not in self._data:
            return None
        value = self._data.pop(key)
        self._data[key] = value
        return value

    def set(self, key: str, value: Optional[str]) -> None:
        if key in self._data:
            self._data.pop(key)
        elif len(self._data) >= self.maxsize:
            self._data.popitem(last=False)
        self._data[key] = value


class LyricsPlugin(LyricsProviderPlugin):
    """Lyrics plugin that tries multiple providers and caches results."""

    def __init__(self, cache_size: int = 128) -> None:
        self.providers: list[LyricsProviderPlugin] = [
            LyricsOvhProvider(),
        ]
        try:
            from .genius import GeniusPlugin

            self.providers.append(GeniusPlugin())
        except Exception:  # pragma: no cover - import failure
            pass
        try:
            from .musixmatch import MusixmatchPlugin

            self.providers.append(MusixmatchPlugin())
        except Exception:  # pragma: no cover - import failure
            pass

        self.cache = _LRUCache(cache_size)

    async def open(self) -> None:
        for provider in self.providers:
            await provider.open()

    async def close(self) -> None:
        for provider in self.providers:
            await provider.close()

    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Return lyrics for ``artist`` and ``title`` using available providers."""

        key = f"{artist.lower()}::{title.lower()}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        for provider in self.providers:
            lyrics = await provider.get_lyrics(artist, title)
            if lyrics:
                self.cache.set(key, lyrics)
                return lyrics

        self.cache.set(key, None)
        return None
