"""Asynchronous Qobuz API wrapper for the legacy :mod:`fla` package."""

from __future__ import annotations

import os
from typing import Any, Optional

import aiohttp
import keyring

BASE_URL = "https://www.qobuz.com/api.json/0.2/"


class QobuzAPI:
    """Minimal async client for a subset of the Qobuz API."""

    def __init__(
        self, app_id: Optional[str] = None, app_secret: Optional[str] = None
    ) -> None:
        self.app_id = app_id or os.getenv("QOBUZ_APP_ID") or ""
        self.app_secret = app_secret or os.getenv("QOBUZ_APP_SECRET") or ""
        self.token = os.getenv("QOBUZ_TOKEN")
        self.user_auth_token: str | None = None
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "QobuzAPI":
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

    async def authenticate(self) -> None:
        """Ensure an authentication token is available."""
        if not self.user_auth_token:
            self.user_auth_token = self.token or keyring.get_password(
                "flaccid_qobuz", "token"
            )

    async def _request(self, endpoint: str, **params: Any) -> Any:
        session = await self._get_session()
        params.setdefault("app_id", self.app_id)
        if self.user_auth_token:
            params.setdefault("user_auth_token", self.user_auth_token)
        async with session.get(BASE_URL + endpoint, params=params) as resp:
            return await resp.json()

    async def search(self, query: str) -> Any:
        """Search Qobuz for tracks matching *query*."""
        await self.authenticate()
        return await self._request("search", query=query)

    async def get_metadata(self, track_id: str) -> Any:
        """Retrieve metadata for a track by *track_id*."""
        await self.authenticate()
        return await self._request("track/get", track_id=track_id)
