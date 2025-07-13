"""Unit tests for :mod:`fla.shared` asynchronous helpers."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Ensure src directory is on path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
        from fla.shared.apple_api import AppleAPI
        from fla.shared.config import Config
        from fla.shared.metadata_utils import (
            build_search_query,
            get_existing_metadata,
            validate_flac_file,
        )
        from fla.shared.qobuz_api import QobuzAPI


class TestConfig:
    """Configuration helper tests."""

    def test_config_initialization(self) -> None:
        cfg = Config()
        assert cfg._loaded is True

    def test_get_default_values(self) -> None:
        cfg = Config()
        assert cfg.get("MISSING", "x") == "x"
        assert cfg.get_bool("MISSING_BOOL", False) is False
        assert cfg.get_int("MISSING_INT", 3) == 3

    @patch.dict(os.environ, {"BOOL_VAL": "true"})
    def test_get_bool_values(self) -> None:
        cfg = Config()
        assert cfg.get_bool("BOOL_VAL") is True

    @patch.dict(os.environ, {"INT_VAL": "123"})
    def test_get_int_values(self) -> None:
        cfg = Config()
        assert cfg.get_int("INT_VAL") == 123


class TestQobuzAPI:
    """Async Qobuz API wrapper tests."""

    def test_initialization(self) -> None:
        api = QobuzAPI()
        assert api.session is None
        assert api.user_auth_token is None

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        async with QobuzAPI() as api:
            assert api.session is not None

    @pytest.mark.asyncio
    async def test_session_creation(self) -> None:
        api = QobuzAPI()
        session = await api._get_session()
        assert session is not None
        await api.close()

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_search_mock(self, mock_get: AsyncMock) -> None:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {"tracks": {"items": [{"id": "1"}]}}
        mock_get.return_value.__aenter__.return_value = mock_resp

        api = QobuzAPI()
        api.user_auth_token = "tok"
        result = await api.search("test")
        assert "tracks" in result
        await api.close()

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_metadata_mock(self, mock_get: AsyncMock) -> None:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {"id": "1", "title": "A"}
        mock_get.return_value.__aenter__.return_value = mock_resp

        api = QobuzAPI()
        api.user_auth_token = "tok"
        data = await api.get_metadata("1")
        assert data["id"] == "1"
        await api.close()


class TestAppleAPI:
    """Async Apple API wrapper tests."""

    def test_initialization(self) -> None:
        api = AppleAPI()
        assert api.session is None
        assert api.developer_token is None

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        async with AppleAPI() as api:
            assert api.session is not None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_itunes_search_mock(self, mock_get: AsyncMock) -> None:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {"results": [{"trackId": 1}]}
        mock_get.return_value.__aenter__.return_value = mock_resp

        api = AppleAPI()
        data = await api.search("hello")
        assert "results" in data
        await api.close()

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_metadata_mock(self, mock_get: AsyncMock) -> None:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {"results": [{"trackId": 1}]}
        mock_get.return_value.__aenter__.return_value = mock_resp

        api = AppleAPI()
        data = await api.get_metadata("1")
        assert "results" in data
        await api.close()


class TestMetadataUtils:
    """Helpers for manipulating metadata."""

    def test_validate_flac_file_nonexistent(self) -> None:
        assert validate_flac_file("/nope.flac") is False

    def test_validate_flac_file_wrong_extension(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            assert validate_flac_file(tmp.name) is False

    def test_build_search_query_with_both(self) -> None:
        meta = {"title": "Song", "artist": "Artist"}
        assert build_search_query(meta) == "Artist Song"

    def test_build_search_query_empty(self) -> None:
        assert build_search_query({}) == ""

    def test_get_existing_metadata_nonexistent(self) -> None:
        assert get_existing_metadata("/missing.flac") == {}
