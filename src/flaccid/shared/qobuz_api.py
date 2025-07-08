import aiohttp
import asyncio
import os
import keyring
import time
from typing import Optional, Dict, Any
from rich.console import Console

console = Console()

class QobuzAPI:
    BASE_URL = "https://www.qobuz.com/api.json/0.2"
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, rate_limit_delay: float = 0.1):
        self.session = None
        self.user_auth_token = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

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

    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()

    async def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Make a request with retry logic and rate limiting."""
        await self._rate_limit()
        
        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                
                if method.upper() == "GET":
                    async with session.get(url, **kwargs) as resp:
                        return await self._handle_response(resp)
                elif method.upper() == "POST":
                    async with session.post(url, **kwargs) as resp:
                        return await self._handle_response(resp)
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    console.print(f"❌ Request failed after {self.max_retries} attempts: {e}", style="red")
                    return None
                
                delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                console.print(f"🔄 Request failed, retrying in {delay:.1f}s... (attempt {attempt + 1}/{self.max_retries})", style="yellow")
                await asyncio.sleep(delay)
        
        return None

    async def _handle_response(self, resp: aiohttp.ClientResponse) -> Optional[Dict[Any, Any]]:
        """Handle HTTP response with proper error handling."""
        if resp.status == 200:
            return await resp.json()
        elif resp.status == 401:
            # Token expired, will be handled by calling method
            return {"_auth_error": True}
        elif resp.status == 429:  # Rate limited
            console.print("⚠️  Rate limited by Qobuz API", style="yellow")
            retry_after = int(resp.headers.get("Retry-After", 60))
            console.print(f"🔄 Waiting {retry_after} seconds before retry...", style="yellow")
            await asyncio.sleep(retry_after)
            return {"_rate_limited": True}
        else:
            error_text = await resp.text()
            console.print(f"❌ API request failed: {resp.status} - {error_text}", style="red")
            return None

    async def authenticate(self):
        """Authenticate with Qobuz using stored credentials."""
        username = keyring.get_password("flaccid-qobuz", "username")
        password = keyring.get_password("flaccid-qobuz", "password")

        if not username or not password:
            console.print("❌ Qobuz credentials not found. Run 'fla set auth qobuz' first.", style="red")
            raise RuntimeError("Missing Qobuz credentials")

        auth_data = {
            "app_id": self.app_id,
            "username": username,
            "password": password,
            "device_id": "flaccid-cli"
        }

        result = await self._make_request("POST", f"{self.BASE_URL}/user/login", data=auth_data)
        
        if result:
            self.user_auth_token = result.get("user_auth_token")
            if not self.user_auth_token:
                raise RuntimeError("Failed to get user auth token from Qobuz")
        else:
            raise RuntimeError("Qobuz authentication failed")

    async def search(self, query: str, limit: int = 5):
        """Search for tracks on Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "limit": limit,
            "query": query,
            "type": "track"
        }

        result = await self._make_request("GET", f"{self.BASE_URL}/catalog/search", params=params)
        
        if result and result.get("_auth_error"):
            # Token expired, re-authenticate and retry
            console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
            self.user_auth_token = None
            await self.authenticate()
            params["user_auth_token"] = self.user_auth_token
            result = await self._make_request("GET", f"{self.BASE_URL}/catalog/search", params=params)
        
        return result

    async def get_track_metadata(self, track_id: str):
        """Get detailed track metadata from Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "track_id": track_id,
        }

        result = await self._make_request("GET", f"{self.BASE_URL}/track/get", params=params)
        
        if result and result.get("_auth_error"):
            console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
            self.user_auth_token = None
            await self.authenticate()
            params["user_auth_token"] = self.user_auth_token
            result = await self._make_request("GET", f"{self.BASE_URL}/track/get", params=params)
        
        return result

    async def get_album_metadata(self, album_id: str):
        """Get detailed album metadata from Qobuz."""
        if not self.user_auth_token:
            await self.authenticate()

        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "album_id": album_id,
        }

        result = await self._make_request("GET", f"{self.BASE_URL}/album/get", params=params)
        
        if result and result.get("_auth_error"):
            console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
            self.user_auth_token = None
            await self.authenticate()
            params["user_auth_token"] = self.user_auth_token
            result = await self._make_request("GET", f"{self.BASE_URL}/album/get", params=params)
        
        return result

    async def get_streaming_url(self, track_id: str, quality: str = "MP3_320"):
        """Get streaming URL for a track (requires subscription)."""
        if not self.user_auth_token:
            await self.authenticate()

        params = {
            "app_id": self.app_id,
            "user_auth_token": self.user_auth_token,
            "track_id": track_id,
            "format_id": quality,
        }

        result = await self._make_request("GET", f"{self.BASE_URL}/track/getFileUrl", params=params)
        
        if result and result.get("_auth_error"):
            console.print("🔄 Qobuz token expired, re-authenticating...", style="yellow")
            self.user_auth_token = None
            await self.authenticate()
            params["user_auth_token"] = self.user_auth_token
            result = await self._make_request("GET", f"{self.BASE_URL}/track/getFileUrl", params=params)
        
        return result

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
