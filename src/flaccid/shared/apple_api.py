import aiohttp
import os
import keyring
from rich.console import Console

console = Console()

class AppleAPI:
    BASE_URL = "https://api.music.apple.com/v1/catalog"
    ITUNES_BASE_URL = "https://itunes.apple.com"

    def __init__(self):
        self.session = None
        self.developer_token = None
        self.user_token = None

    @property
    def store(self):
        """Get the store region from environment."""
        return os.getenv("APPLE_STORE", "us")

    @property
    def default_token(self):
        """Get the default token from environment."""
        return os.getenv("APPLE_TOKEN", "your_developer_token")

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _get_tokens(self):
        """Get Apple Music API tokens from keyring or environment."""
        if not self.developer_token:
            # Try keyring first
            self.developer_token = keyring.get_password("flaccid-apple", "developer_token")
            if not self.developer_token:
                # Fall back to environment variable
                self.developer_token = self.TOKEN
                if self.developer_token == "your_developer_token":
                    console.print("⚠️  Apple Music developer token not configured", style="yellow")
                    return False

        if not self.user_token:
            self.user_token = keyring.get_password("flaccid-apple", "user_token")

        return True

    async def search(self, query: str, limit: int = 5):
        """Search Apple Music catalog."""
        await self._get_tokens()

        if not self.developer_token or self.developer_token == "your_developer_token":
            # Fall back to iTunes Search API (no authentication required)
            return await self._itunes_search(query, limit)

        session = await self._get_session()
        url = f"{self.BASE_URL}/{self.STORE}/search"

        headers = {"Authorization": f"Bearer {self.developer_token}"}
        if self.user_token:
            headers["Music-User-Token"] = self.user_token

        params = {
            "term": query,
            "limit": str(limit),
            "types": "songs"
        }

        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                console.print(f"❌ Apple Music search failed: {resp.status}", style="red")
                # Fall back to iTunes Search API
                return await self._itunes_search(query, limit)

    async def _itunes_search(self, query: str, limit: int = 5):
        """Search using iTunes Search API (no authentication required)."""
        session = await self._get_session()
        url = f"{self.ITUNES_BASE_URL}/search"

        params = {
            "term": query,
            "media": "music",
            "entity": "song",
            "limit": str(limit)
        }

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {"results": data.get("results", [])}
            else:
                console.print(f"❌ iTunes search failed: {resp.status}", style="red")
                return None

    async def get_track(self, track_id: str):
        """Get track details by ID."""
        await self._get_tokens()

        if not self.developer_token or self.developer_token == "your_developer_token":
            console.print("⚠️  Apple Music developer token required for track lookup", style="yellow")
            return None

        session = await self._get_session()
        url = f"{self.BASE_URL}/{self.STORE}/songs/{track_id}"

        headers = {"Authorization": f"Bearer {self.developer_token}"}
        if self.user_token:
            headers["Music-User-Token"] = self.user_token

        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                console.print(f"❌ Apple Music track lookup failed: {resp.status}", style="red")
                return None

    async def lookup_by_isrc(self, isrc: str):
        """Look up track by ISRC using iTunes Search API."""
        session = await self._get_session()

        # Clean ISRC (remove any dashes or spaces)
        clean_isrc = isrc.replace("-", "").replace(" ", "").upper()

        params = {
            "term": clean_isrc,
            "media": "music",
            "entity": "song",
            "limit": "50"
        }

        async with session.get(f"{self.ITUNES_BASE_URL}/search", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()

                # Look for exact ISRC match in results
                for result in data.get("results", []):
                    if result.get("isrc", "").replace("-", "").upper() == clean_isrc:
                        return result

                # If no exact match, return first result if available
                if data.get("results"):
                    return data["results"][0]

                return None
            else:
                console.print(f"❌ iTunes ISRC lookup failed: {resp.status}", style="red")
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
