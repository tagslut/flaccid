from pathlib import Path
from typer.testing import CliRunner

from fla.__main__ import app
import flaccid.commands.lib as lib_cli

runner = CliRunner()


def test_lib_fails_without_args():
    result = runner.invoke(app, ["lib"])
    assert result.exit_code != 0


def test_lib_scan_invokes_core(monkeypatch, tmp_path):
    called = {}

    monkeypatch.setattr(lib_cli.library, "scan_directory", lambda d: [tmp_path / "a.flac"])

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
