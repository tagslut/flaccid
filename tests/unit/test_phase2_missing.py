"""Tests for Phase 2 features that are currently unimplemented."""

from __future__ import annotations

import pytest


@pytest.mark.xfail(reason="metadata.cascade not implemented")
def test_metadata_cascade_merges() -> None:
    """``cascade`` should merge metadata objects with priority order."""
    from flaccid.core import metadata

    m1 = metadata.TrackMetadata(title="A", artist="", album="")
    m2 = metadata.TrackMetadata(title="", artist="B", album="C")
    merged = metadata.cascade(m1, m2)  # type: ignore[attr-defined]
    assert merged.title == "A"
    assert merged.artist == "B"
    assert merged.album == "C"


def test_dynaconf_configuration_loading(tmp_path) -> None:
    """Configuration should load from TOML using Dynaconf and Pydantic."""
    from flaccid.core import config  # type: ignore

    cfg = tmp_path / "settings.toml"
    cfg.write_text("[default]\nQOBUZ_APP_ID='abc'\n")
    settings = config.load_settings(cfg)  # type: ignore[attr-defined]
    assert settings.qobuz.app_id == "abc"


@pytest.mark.skip(reason="watch_library stub not implemented")
def test_watch_library_detects_changes(tmp_path) -> None:
    """Watcher should index newly created FLAC files."""
    from flaccid.core import library

    db = tmp_path / "lib.db"
    flac = tmp_path / "song.flac"
    flac.write_text("data")

    library.watch_library(tmp_path, db)  # type: ignore[attr-defined]
    engine, tracks = library._init_db(db)  # type: ignore
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    with Session(engine) as sess:
        paths = {row.path for row in sess.execute(select(tracks.c.path))}
    assert str(flac) in paths


@pytest.mark.xfail(reason="Plugin download not fully implemented")
@pytest.mark.asyncio
async def test_qobuz_plugin_download(tmp_path) -> None:
    """Qobuz plugin should download a track to the given destination."""
    from flaccid.plugins.qobuz import QobuzPlugin

    dest = tmp_path / "file.flac"
    plugin = QobuzPlugin(app_id="id", token="token")

    async def _run() -> bool:
        async with plugin:
            return await plugin.download_track("123", dest)

    success = await _run()  # type: ignore[misc]
    assert success and dest.exists()


@pytest.mark.xfail(reason="Tidal authentication not implemented")
@pytest.mark.asyncio
async def test_tidal_plugin_authentication() -> None:
    """Tidal plugin should authenticate with username and password."""
    from flaccid.plugins.tidal import TidalPlugin

    plugin = TidalPlugin()

    async def _run() -> str:
        async with plugin:
            return await plugin.login("user", "pw")  # type: ignore[attr-defined]

    token = await _run()  # type: ignore[misc]
    assert token
