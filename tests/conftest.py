#!/usr/bin/env python3
"""
Test configuration for pytest.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def temp_dir():
    """
    Create a temporary directory that exists for the entire test session.

    This avoids creating too many temp directories which can cause issues
    when disk space is limited.
    """
    # Create a session-scoped temporary directory
    temp_path = Path(tempfile.mkdtemp(prefix="flaccid_test_"))
    yield temp_path
    # Clean up after tests
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_file(temp_dir):
    """
    Create a temporary file within the session temp directory.
    """
    temp_file_path = temp_dir / f"test_file_{os.urandom(4).hex()}.txt"
    temp_file_path.touch()
    yield temp_file_path
    # Clean up the file
    if temp_file_path.exists():
        temp_file_path.unlink()


@pytest.fixture
def temp_flac_file(temp_dir):
    """
    Create a temporary FLAC file within the session temp directory.
    """
    temp_flac_path = temp_dir / f"test_file_{os.urandom(4).hex()}.flac"
    temp_flac_path.touch()
    yield temp_flac_path
    # Clean up the file
    if temp_flac_path.exists():
        temp_flac_path.unlink()


@pytest.fixture
def lyrics_ovh_response() -> dict[str, str]:
    """Return sample lyrics API response."""

    import json
    from pathlib import Path

    fixture = Path(__file__).parent / "fixtures" / "lyrics_ovh.json"
    with fixture.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def tidal_track_response() -> dict[str, object]:
    """Return sample Tidal track response."""

    import json
    from pathlib import Path

    fixture = Path(__file__).parent / "fixtures" / "tidal_track.json"
    with fixture.open(encoding="utf-8") as fh:
        return json.load(fh)
