from __future__ import annotations

"""Tests for Dynaconf-based configuration loader."""

import os
from pathlib import Path
from unittest.mock import patch

from flaccid.core.config import get_precedence_order, load_settings, Settings


def test_load_from_environment() -> None:
    """Settings should load values from environment variables."""
    with patch.dict(os.environ, {"QOBUZ_APP_ID": "id", "QOBUZ_TOKEN": "tok"}):
        settings = load_settings()
        assert settings.qobuz.app_id == "id"
        assert settings.qobuz.token == "tok"


def test_load_from_file(tmp_path: Path) -> None:
    """Settings should load from a TOML file."""
    cfg = tmp_path / "settings.toml"
    cfg.write_text(
        """\
[default]
QOBUZ_APP_ID = 'file_id'
QOBUZ_TOKEN = 'file_tok'
"""
    )
    settings = load_settings(cfg)
    assert settings.qobuz.app_id == "file_id"
    assert settings.qobuz.token == "file_tok"


def test_load_plugin_precedence(tmp_path: Path) -> None:
    cfg = tmp_path / "settings.toml"
    cfg.write_text(
        """\
[default]
PLUGIN_PRECEDENCE = 'a,b'
"""
    )
    settings = load_settings(cfg)
    assert settings.plugin_precedence == ["a", "b"]


def test_get_precedence_order_custom() -> None:
    settings = Settings(plugin_precedence=["b", "a"])
    order = get_precedence_order(["a", "b", "c"], settings=settings)
    assert order == ["b", "a", "c"]
