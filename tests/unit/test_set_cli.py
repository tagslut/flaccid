from typer.testing import CliRunner

import json
from pathlib import Path

import flaccid.set.cli as set_cli
from flaccid.cli import app as cli_app

runner = CliRunner()


def test_auth_stores_credentials(monkeypatch):
    called = {}

    def fake_set_password(service: str, provider: str, token: str) -> None:
        called["args"] = (service, provider, token)

    monkeypatch.setattr(set_cli.keyring, "set_password", fake_set_password)

    result = runner.invoke(cli_app, ["set", "auth", "qobuz"], input="secret\n")

    assert result.exit_code == 0
    assert called["args"] == ("flaccid", "qobuz", "secret")
    assert "API key" in result.stdout
    assert "Credentials saved." in result.stdout


def test_path_saves_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    lib = tmp_path / "lib"
    cache = tmp_path / "cache"

    result = runner.invoke(
        cli_app,
        ["set", "path", "--library", str(lib), "--cache", str(cache)],
    )

    config = tmp_path / ".flaccid" / "paths.json"

    assert result.exit_code == 0
    saved = json.loads(config.read_text())
    assert saved["library"].endswith("lib")
    assert saved["cache"].endswith("cache")


def test_path_saves_defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = runner.invoke(cli_app, ["set", "path"])

    config = tmp_path / ".flaccid" / "paths.json"

    assert result.exit_code == 0
    saved = json.loads(config.read_text())
    assert saved == {}


def test_path_updates_existing(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    lib1 = tmp_path / "lib1"
    cache1 = tmp_path / "cache1"

    runner.invoke(
        cli_app,
        ["set", "path", "--library", str(lib1), "--cache", str(cache1)],
    )

    lib2 = tmp_path / "lib2"
    runner.invoke(cli_app, ["set", "path", "--library", str(lib2)])

    config = tmp_path / ".flaccid" / "paths.json"
    data = json.loads(config.read_text())

    assert data["library"].endswith("lib2")
    assert data["cache"].endswith("cache1")
