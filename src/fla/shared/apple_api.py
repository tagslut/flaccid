"""Asynchronous Apple Music API wrapper used by the legacy :mod:`fla` package."""

from __future__ import annotations

import os
from typing import Any, Optional

import aiohttp

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"


class AppleAPI:
    """Small async wrapper around the public iTunes search API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("APPLE_API_KEY")
        self.developer_token = None
        self.store = os.getenv("APPLE_STORE", "us")
        self.default_token = os.getenv("APPLE_TOKEN")
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AppleAPI":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _itunes_search(self, query: str) -> dict[str, Any]:
        """Search iTunes for *query* and return the JSON payload."""
        session = await self._get_session()
        async with session.get(
            ITUNES_SEARCH_URL, params={"term": query, "entity": "song"}
        ) as resp:
            return await resp.json()

    async def search(self, query: str) -> dict[str, Any]:
        """Search for songs matching *query*."""
        return await self._itunes_search(query)

    async def get_metadata(self, track_id: str) -> dict[str, Any]:
        """Look up metadata for a track by its ID."""
        session = await self._get_session()
        async with session.get(
            ITUNES_LOOKUP_URL, params={"id": track_id, "entity": "song"}
        ) as resp:
            return await resp.json()
