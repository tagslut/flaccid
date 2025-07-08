import aiohttp
import asyncio
import os
import keyring
from rich.console import Console

console = Console()

class QobuzAPI:
    BASE_URL = "https://www.qobuz.com/api.json/0.2"

    def __init__(self):
        self.session = None
        self.user_auth_token = None

    @property
    def app_id(self):
        """Get the app ID from environment or class constant."""
        return os.getenv("QOBUZ_APP_ID", "your_app_id_here")

    @property
    def token(self):
        """Get the token from environment or class constant."""
        return os.getenv("QOBUZ_TOKEN", "your_auth_token_here")

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def authenticate(self):
        """Authenticate with Qobuz using stored credentials."""
        username = keyring.get_password("flaccid-qobuz", "username")
        password = keyring.get_password("flaccid-qobuz", "password")

        if not username or not password:
            console.print("❌ Qobuz credentials not found. Run 'fla set auth qobuz' first.", style="red")
            raise RuntimeError("Missing Qobuz credentials")

        session = await self._get_session()

        auth_data = {
            "app_id": self.app_id,
            "username": username,
            "password": password,
            "device_id": "flaccid-cli"
        }

        async with session.post(f"{self.BASE_URL}/user/login", data=auth_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.user_auth_token = result.get("user_auth_token")
                if not self.user_auth_token:
                    raise RuntimeError("Failed to get user auth token from Qobuz")
            else:
                error_text = await resp.text()
                raise RuntimeError(f"Qobuz auth failed: {resp.status} - {error_text}")

    async def search(self, query: str, limit: int = 5):
        """Search for tracks on Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        session = await self._get_session()
        url = f"{self.BASE_URL}/catalog/search"
        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "limit": limit,
            "query": query,
            "type": "track"
        }

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                # Token might be expired, try to re-authenticate
                console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
                self.user_auth_token = None
                await self.authenticate()
                return await self.search(query, limit)
            else:
                console.print(f"❌ Qobuz search failed: {resp.status}", style="red")
                return None

    async def get_track_metadata(self, track_id: str):
        """Get detailed track metadata from Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        session = await self._get_session()
        url = f"{self.BASE_URL}/track/get"
        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "track_id": track_id,
        }

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                # Token might be expired, try to re-authenticate
                console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
                self.user_auth_token = None
                await self.authenticate()
                return await self.get_track_metadata(track_id)
            else:
                console.print(f"❌ Qobuz track fetch failed: {resp.status}", style="red")
                return None

    async def get_album_metadata(self, album_id: str):
        """Get detailed album metadata from Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        session = await self._get_session()
        url = f"{self.BASE_URL}/album/get"
        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "album_id": album_id,
        }

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
                self.user_auth_token = None
                await self.authenticate()
                return await self.get_album_metadata(album_id)
            else:
                console.print(f"❌ Qobuz album fetch failed: {resp.status}", style="red")
                return None

    async def get_streaming_url(self, track_id: str, quality: str = "MP3_320"):
        """Get streaming URL for a track (requires subscription)."""
        if not self.user_auth_token:
            await self.authenticate()

        session = await self._get_session()
        url = f"{self.BASE_URL}/track/getFileUrl"
        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "track_id": track_id,
            "format_id": quality,
        }

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
                self.user_auth_token = None
                await self.authenticate()
                return await self.get_streaming_url(track_id, quality)
            else:
                console.print(f"❌ Qobuz streaming URL failed: {resp.status}", style="red")
                return None

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
