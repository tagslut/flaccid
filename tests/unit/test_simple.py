"""Tests for configuration and metadata utility helpers."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from flaccid.shared import metadata_utils
from flaccid.shared.config import Config


def test_config_type_parsing() -> None:
    """Values should be parsed into the correct Python types."""
    with patch.dict(os.environ, {"FLAG": "yes", "COUNT": "bad"}):
        cfg = Config()
        assert cfg.get_bool("FLAG") is True
        assert cfg.get_int("COUNT", 7) == 7


def test_validate_flac_file(tmp_path: Path) -> None:
    """``validate_flac_file`` should accept only existing ``.flac`` files."""
    flac = tmp_path / "song.flac"
    mp3 = tmp_path / "song.mp3"
    flac.write_text("data")
    mp3.write_text("data")

    assert metadata_utils.validate_flac_file(str(flac)) is True
    assert metadata_utils.validate_flac_file(str(mp3)) is False


def test_metadata_helpers(tmp_path: Path) -> None:
    """Utility functions should produce normalized metadata."""
    assert metadata_utils.normalize_artist("  The Artist  ") == "the artist"

    flac = tmp_path / "x.flac"
    flac.write_text("data")

    existing = metadata_utils.get_existing_metadata(str(flac))
    assert existing == {"artist": "Unknown Artist", "title": "Unknown Title"}
    assert metadata_utils.extract_isrc_from_flac(str(flac)) == "UNKNOWN-ISRC"

    meta = {"artist": "A", "title": "B"}
    assert metadata_utils.build_search_query(meta) == "A B"
    assert metadata_utils.build_search_query({"title": "B"}) == "B"
    assert metadata_utils.build_search_query({}) == ""
