"""
Simple tests for shared API modules.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from flaccid.shared import config

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_basic():
    """Test basic configuration functionality."""
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        cfg = config.yesConfig()

        assert cfg.get("FOO", "bar") == "bar"
        assert cfg.get("TEST_VAR") == "test_value"
        assert cfg.get("NONEXISTENT", "default") == "default"


def test_metadata_utils_basic():
    """Test basic metadata utilities."""
    from flaccid.shared.metadata_utils import build_search_query, validate_flac_file

    # Test file validation
    assert validate_flac_file("/nonexistent/file.flac") is False
    assert validate_flac_file("/nonexistent/file.mp3") is False

    # Test query building
    metadata = {"title": "Test Song", "artist": "Test Artist"}
    query = build_search_query(metadata)
    assert query == "Test Artist Test Song"

    metadata = {"title": "Test Song"}
    query = build_search_query(metadata)
    assert query == "Test Song"

    metadata = {}
    query = build_search_query(metadata)
    assert query == ""


@pytest.mark.asyncio
async def test_qobuz_api_basic():
    """Test basic Qobuz API functionality."""
    with patch.dict(
        os.environ, {"QOBUZ_APP_ID": "test_id", "QOBUZ_TOKEN": "test_token"}
    ):
        with patch("keyring.get_password", return_value=None):
            from flaccid.shared.qobuz_api import QobuzAPI

            api = QobuzAPI()
            assert api.app_id == "test_id"
            assert api.token == "test_token"

            # Test context manager
            async with QobuzAPI() as api_ctx:
                assert api_ctx is not None


@pytest.mark.asyncio
async def test_apple_api_basic():
    """Test basic Apple API functionality."""
    with patch.dict(os.environ, {"APPLE_TOKEN": "test_token", "APPLE_STORE": "us"}):
        with patch("keyring.get_password", return_value=None):
            from flaccid.shared.apple_api import AppleAPI

            api = AppleAPI()
            assert api.store == "us"
            assert api.default_token == "test_token"

            # Test context manager
            async with AppleAPI() as api_ctx:
                assert api_ctx is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
