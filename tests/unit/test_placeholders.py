from __future__ import annotations

"""Unit tests for path and filename placeholder helpers."""

import json
from pathlib import Path
import asyncio

from mutagen.flac import FLAC

import flaccid.cli.placeholders as placeholders


class AsyncContext:
    def __init__(self, result: dict) -> None:
        self.result = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def search(self, query: str):
        self.query = query
        return self.result

    async def _itunes_search(self, query: str):
        self.query = query
        return self.result


def test_fetch_metadata_qobuz(monkeypatch, tmp_path):
    flac = tmp_path / "t.flac"
    flac.write_text("data")

    monkeypatch.setattr(
        placeholders,
        "get_existing_metadata",
        lambda path: {"artist": "A", "title": "B"},
    )
    monkeypatch.setattr(placeholders, "build_search_query", lambda meta: "A B")

    called = {}

    class FakePlugin(AsyncContext):
        async def search_track(self, query: str):
            called["query"] = query
            return self.result

    monkeypatch.setattr(
        placeholders,
        "get_provider",
        lambda name: (lambda: FakePlugin({"ok": True})),
    )

    result = placeholders.fetch_metadata(flac, "qobuz")
    assert result == {"ok": True}
    assert called["query"] == "A B"


def test_apply_metadata(monkeypatch, tmp_path):
    flac = tmp_path / "t.flac"
    flac.write_text("data")
    meta_file = tmp_path / "meta.json"
    meta_file.write_text(
        json.dumps(
            {
                "title": "Song",
                "artist": "Artist",
                "album": "A",
                "track_number": 1,
                "disc_number": 1,
            }
        )
    )

    called = {"write": []}

    async def _dummy_write_tags(file, metadata, **kwargs):
        called["write"].append(file)
        return str(file)

    def wrapper(*args, **kwargs):
        coro = _dummy_write_tags(*args, **kwargs)
        called["is_coro"] = asyncio.iscoroutine(coro)
        return coro

    monkeypatch.setattr(placeholders, "write_tags", wrapper)

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
    assert called["is_coro"] is True


def test_store_credentials(monkeypatch):
    called = {}

    def fake_set(service: str, name: str, value: str) -> None:
        called.setdefault("calls", []).append((service, name, value))

    monkeypatch.setattr(
        placeholders, "keyring", type("KR", (), {"set_password": fake_set})
    )

    placeholders.store_credentials("qobuz", "key123", "secret456")

    assert called["calls"] == [
        ("flaccid", "qobuz_key", "key123"),
        ("flaccid", "qobuz_secret", "secret456"),
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
