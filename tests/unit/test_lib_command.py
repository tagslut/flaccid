"""Unit tests for the ``flaccid lib`` CLI command group."""

from pathlib import Path

from typer.testing import CliRunner

import flaccid.commands.lib as lib_cli
from fla.__main__ import app

runner = CliRunner()


def test_lib_fails_without_args():
    result = runner.invoke(app, ["lib"])
    assert result.exit_code != 0


def test_lib_scan_invokes_core(monkeypatch, tmp_path):
    called = {}

    monkeypatch.setattr(
        lib_cli.library, "scan_directory", lambda d: [tmp_path / "a.flac"]
    )

    def fake_index(db, files):
        called["args"] = (db, files)

    monkeypatch.setattr(lib_cli.library, "index_changed_files", fake_index)

    result = runner.invoke(app, ["library", "scan", str(tmp_path)])

    assert result.exit_code == 0
    assert called["args"][0] == Path("library.db")


def test_lib_scan_watch(monkeypatch, tmp_path):
    called = {}

    monkeypatch.setattr(lib_cli.library, "scan_directory", lambda d: [])
    monkeypatch.setattr(lib_cli.library, "index_changed_files", lambda db, files: None)

    def fake_watch(directory, db):
        called["args"] = (directory, db)

    monkeypatch.setattr(lib_cli.library, "watch_library", fake_watch)

    result = runner.invoke(app, ["library", "scan", str(tmp_path), "--watch"])

    assert result.exit_code == 0
    assert called["args"] == (tmp_path, Path("library.db"))


def test_lib_search_invokes_core(monkeypatch):
    called = {}

    def fake_search(db, query, sort=None, limit=None, offset=0):
        called["args"] = (db, query, sort, limit, offset)
        return []

    monkeypatch.setattr(lib_cli.library, "search_library", fake_search)

    result = runner.invoke(
        app,
        [
            "library",
            "search",
            "--filter",
            "beatles",
            "--sort",
            "title",
            "--limit",
            "5",
            "--offset",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert called["args"] == (
        Path("library.db"),
        "beatles",
        "title",
        5,
        1,
    )


def test_lib_missing_invokes_core(monkeypatch):
    called = {}

    def fake_report(db):
        called["db"] = db
        return []

    monkeypatch.setattr(lib_cli.library, "report_missing_metadata", fake_report)

    result = runner.invoke(app, ["library", "missing"])

    assert result.exit_code == 0
    assert called["db"] == Path("library.db")


def test_lib_view_invokes_search(monkeypatch):
    called = {}

    def fake_search(db, query, sort=None, limit=None, offset=0):
        called["args"] = (db, query, sort, limit, offset)
        return [{"path": "x.flac", "title": "t", "artist": "a", "album": "b"}]

    class FakeFLAC(dict):
        def __init__(self, path: str) -> None:  # noqa: D401 - simple stub
            self.path = path

        def get(self, key, default=None):
            return []

        @property
        def pictures(self):  # pragma: no cover - not used
            return []

    monkeypatch.setattr(lib_cli.library, "search_library", fake_search)
    monkeypatch.setattr(lib_cli, "FLAC", FakeFLAC)

    result = runner.invoke(app, ["library", "view", "--filter", "x", "--limit", "2"])

    assert result.exit_code == 0
    assert called["args"] == (Path("library.db"), "x", None, 2, 0)


def test_lib_view_filters(monkeypatch):
    rows = [
        {"path": "a.flac", "title": "A", "artist": "aa", "album": "z"},
        {"path": "b.flac", "title": "B", "artist": "bb", "album": "z"},
    ]

    monkeypatch.setattr(lib_cli.library, "search_library", lambda *a, **k: rows)

    class FakeFLAC:
        def __init__(self, path: str) -> None:
            self.path = path

        def get(self, key, default=None):
            if key == "lyrics":
                return ["l"] if self.path == "a.flac" else []
            return []

        @property
        def pictures(self):
            return [b"img"] if self.path == "b.flac" else []

    monkeypatch.setattr(lib_cli, "FLAC", FakeFLAC)

    result = runner.invoke(app, ["library", "view", "--missing-lyrics"])
    assert result.exit_code == 0
    assert "b.flac" in result.output
    assert "a.flac" not in result.output

    result = runner.invoke(app, ["library", "view", "--has-artwork"])
    assert result.exit_code == 0
    assert "b.flac" in result.output
    assert "a.flac" not in result.output
