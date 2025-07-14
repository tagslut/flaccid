"""
Apple Music API client with iTunes fallback.
"""

from typing import Optional

import aiohttp

from flaccid.core.config import load_settings


class AppleAPI:
    def __init__(self, api_key: Optional[str] = None):
        settings = load_settings()
        self.api_key = api_key or "default_api_key"
        self.developer_token = None
        self.store = settings.apple.store
        self.default_token = settings.apple.developer_token or "default_token"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _itunes_search(self, query: str):
        """Search for a track on iTunes."""
        await self._get_session()
        # Placeholder implementation
        return {
            "results": [
                {
                    "trackId": 12345,
                    "trackName": "Test Track",
                    "artistName": "Test Artist",
                    "collectionName": "Test Album",
                }
            ]
        }

    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    def search(self, query: str):
        """Search for a track on Apple Music."""

    def get_metadata(self, track_id: str):
        """Retrieve metadata for a given track ID."""
