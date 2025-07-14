import importlib
from pathlib import Path

import pytest

from flaccid.plugins.base import TrackMetadata


@pytest.mark.parametrize(
    "module_name,plugin_attr",
    [
        ("flaccid.tag.qobuz", "QobuzPlugin"),
        ("flaccid.tag.apple", "AppleMusicPlugin"),
        ("flaccid.tag.beatport", "BeatportPlugin"),
        ("flaccid.tag.discogs", "DiscogsPlugin"),
    ],
)
def test_tag_from_id_invokes_plugins(
    module_name: str, plugin_attr: str, tmp_path: Path, monkeypatch
):
    module = importlib.import_module(module_name)

    file = tmp_path / "song.flac"
    file.write_text("data")

    meta = TrackMetadata(
        title="S",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )
    from typing import Any

    called: dict[str, Any] = {}

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_track(self, track_id: str):
            called["id"] = track_id
            return meta

    class FakeLyrics:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_lyrics(
            self, artist: str, title: str
        ):  # pragma: no cover - not used
            return "la"

    async def fake_fetch(
        path: Path, data: TrackMetadata, lyrics_plugin=None, art_data=None
    ):
        called["fetch"] = (path, data)

    monkeypatch.setattr(module, plugin_attr, lambda: FakePlugin())
    monkeypatch.setattr(module, "LyricsPlugin", lambda: FakeLyrics())
    monkeypatch.setattr(module.metadata, "fetch_and_tag", fake_fetch)

    module.tag_from_id(file, "123")

    assert called["id"] == "123"
    assert called["fetch"] == (file, meta)
