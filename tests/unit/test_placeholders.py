from __future__ import annotations

import json
from pathlib import Path


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

    fake_api = AsyncContext({"ok": True})
    monkeypatch.setattr(placeholders, "QobuzAPI", lambda: fake_api)

    result = placeholders.fetch_metadata(flac, "qobuz")
    assert result == {"ok": True}
    assert fake_api.query == "A B"


def test_apply_metadata(monkeypatch, tmp_path):
    flac = tmp_path / "t.flac"
    flac.write_text("data")
    meta_file = tmp_path / "meta.json"
    meta_file.write_text(json.dumps({"title": "Song"}))

    saved = {}

    class FakeFLAC(dict):
        def save(self):
            saved["ok"] = True

    monkeypatch.setattr(placeholders, "FLAC", lambda path: FakeFLAC())
    monkeypatch.setattr(placeholders, "confirm", lambda msg: True)

    placeholders.apply_metadata(flac, meta_file, yes=False)

    assert saved.get("ok") is True


def test_store_credentials(monkeypatch):
    called = {}

    def fake_set(service, provider, key):
        called["args"] = (service, provider, key)

    monkeypatch.setattr(
        placeholders, "keyring", type("KR", (), {"set_password": fake_set})
    )
    placeholders.store_credentials("qobuz", "secret")
    assert called["args"] == ("flaccid", "qobuz", "secret")


def test_save_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    data = placeholders.save_paths(Path("lib"), Path("cache"))
    config = tmp_path / ".flaccid" / "paths.json"
    assert config.exists()
    saved = json.loads(config.read_text())
    assert saved == data
    assert saved["library"].endswith("lib")
    assert saved["cache"].endswith("cache")
