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
