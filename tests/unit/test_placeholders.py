import json
from pathlib import Path

import pytest

from flaccid.cli import placeholders
from flaccid.plugins.base import TrackMetadata


def test_apply_metadata(monkeypatch, tmp_path):
    flac = tmp_path / "test.flac"
    flac.touch()

    meta_file = tmp_path / "meta.json"
    meta_file.write_text(
        json.dumps(
            {
                "title": "Song",
                "artist": "Artist",
                "album": "Album",
                "track_number": 1,
                "disc_number": 1,
            }
        )
    )

    called = {}

    async def mock_write_tags(file, metadata):
        called["write"] = (file, metadata)

    # Mock `write_tags` where it is used: in the `placeholders` module.
    # The original test was mocking the wrong target, causing the real function to run.
    monkeypatch.setattr(placeholders, "write_tags", mock_write_tags)

    class FakeLyrics:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_lyrics(self, artist: str, title: str):
            called["lyrics"] = (artist, title)
            return "la"

    monkeypatch.setattr(placeholders, "LyricsPlugin", lambda: FakeLyrics())
    monkeypatch.setattr(placeholders, "confirm", lambda msg: True)

    placeholders.apply_metadata(flac, meta_file, yes=False)

    assert called["write"][0] == flac
    assert called["lyrics"] == ("Artist", "Song")


def test_store_credentials(monkeypatch):
    called = {"calls": []}

    def fake_set(service, provider, value):
        called["calls"].append((service, provider, value))

    monkeypatch.setattr(
        placeholders, "keyring", type("KR", (), {"set_password": fake_set})
    )
    placeholders.store_credentials("qobuz", "key", "secret")
    assert called["calls"] == [
        ("flaccid", "qobuz_key", "key"),
        ("flaccid", "qobuz_secret", "secret"),
    ]


def test_save_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    data = placeholders.save_paths(Path("lib"), Path("cache"))
    config = tmp_path / ".flaccid" / "paths.json"
    assert config.exists()
    saved = json.loads(config.read_text())
    assert saved == data
    assert saved["library"].endswith("lib")
    assert saved["cache"].endswith("cache")
