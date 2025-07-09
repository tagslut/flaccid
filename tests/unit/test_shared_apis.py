"""
Unit tests for shared API modules.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import os
import tempfile
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock the environment variables and keyring before importing
with patch.dict(
    os.environ,
    {
        "QOBUZ_APP_ID": "test_app_id",
        "QOBUZ_TOKEN": "test_token",
        "APPLE_TOKEN": "test_apple_token",
        "APPLE_STORE": "us",
    },
):
    with patch("keyring.get_password", return_value=None):
        from fla.shared.qobuz_api import QobuzAPI
        from fla.shared.apple_api import AppleAPI
        from fla.shared.config import Config
        from fla.shared.metadata_utils import (
            validate_flac_file,
            get_existing_metadata,
            build_search_query,
            extract_isrc_from_flac,
        )


class TestConfig:
    """Test configuration management."""

    def test_config_initialization(self):
        """Test that config initializes correctly."""
        test_config = Config()
        assert test_config is not None
        assert test_config._loaded is True

    def test_get_default_values(self):
        """Test that default values are returned."""
        test_config = Config()
        assert test_config.get("NONEXISTENT_KEY", "default") == "default"
        assert test_config.get_bool("NONEXISTENT_BOOL", False) is False
        assert test_config.get_int("NONEXISTENT_INT", 42) == 42

    @patch.dict(os.environ, {"TEST_BOOL": "true"})
    def test_get_bool_values(self):
        """Test boolean configuration parsing."""
        test_config = Config()
        assert test_config.get_bool("TEST_BOOL") is True

    @patch.dict(os.environ, {"TEST_INT": "123"})
    def test_get_int_values(self):
        """Test integer configuration parsing."""
        test_config = Config()
        assert test_config.get_int("TEST_INT") == 123


class TestQobuzAPI:
    """Test Qobuz API client."""

    def test_initialization(self):
        """Test that QobuzAPI initializes correctly."""
        api = QobuzAPI()
        assert api is not None
        assert api.session is None
        assert api.user_auth_token is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that QobuzAPI works as async context manager."""
        async with QobuzAPI() as api:
            assert api is not None

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test session creation."""
        api = QobuzAPI()
        session = await api._get_session()
        assert session is not None
        await api.close()

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_search_mock(self, mock_get):
        """Test search with mocked response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "tracks": {
                "items": [
                    {
                        "id": "12345",
                        "title": "Test Track",
                        "performer": {"name": "Test Artist"},
                    }
                ]
            }
        }
        mock_get.return_value.__aenter__.return_value = mock_response

        api = QobuzAPI()
        api.user_auth_token = "test_token"  # Mock authenticated state

        result = await api.search("test query")
        assert result is not None
        assert "tracks" in result

        await api.close()


class TestAppleAPI:
    """Test Apple API client."""

    def test_initialization(self):
        """Test that AppleAPI initializes correctly."""
        api = AppleAPI()
        assert api is not None
        assert api.session is None
        assert api.developer_token is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that AppleAPI works as async context manager."""
        async with AppleAPI() as api:
            assert api is not None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_itunes_search_mock(self, mock_get):
        """Test iTunes search with mocked response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "trackId": 12345,
                    "trackName": "Test Track",
                    "artistName": "Test Artist",
                    "collectionName": "Test Album",
                }
            ]
        }
        mock_get.return_value.__aenter__.return_value = mock_response

        api = AppleAPI()
        result = await api._itunes_search("test query")
        assert result is not None
        assert "results" in result

        await api.close()


class TestMetadataUtils:
    """Test metadata utility functions."""

    def test_validate_flac_file_nonexistent(self):
        """Test validation of non-existent file."""
        assert validate_flac_file("/path/to/nonexistent.flac") is False

    def test_validate_flac_file_wrong_extension(self):
        """Test validation of file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp:
            assert validate_flac_file(temp.name) is False

    def test_build_search_query_with_both(self):
        """Test building search query with both title and artist."""
        metadata = {"title": "Test Song", "artist": "Test Artist"}
        query = build_search_query(metadata)
        assert query == "Test Artist Test Song"

    def test_build_search_query_title_only(self):
        """Test building search query with only title."""
        metadata = {"title": "Test Song"}
        query = build_search_query(metadata)
        assert query == "Test Song"

    def test_build_search_query_artist_only(self):
        """Test building search query with only artist."""
        metadata = {"artist": "Test Artist"}
        query = build_search_query(metadata)
        assert query == "Test Artist"

    def test_build_search_query_empty(self):
        """Test building search query with empty metadata."""
        metadata = {}
        query = build_search_query(metadata)
        assert query == ""

    def test_get_existing_metadata_nonexistent(self):
        """Test getting metadata from non-existent file."""
        metadata = get_existing_metadata("/path/to/nonexistent.flac")
        assert metadata == {}


if __name__ == "__main__":
    pytest.main([__file__])
