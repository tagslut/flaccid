"""Unit tests for the ``flaccid set`` CLI utilities."""

from typer.testing import CliRunner

import flaccid.set.cli as set_cli

runner = CliRunner()


def test_auth_stores_credentials(monkeypatch):
    called = {}

    def fake_store_credentials(provider: str, api_key: str) -> None:
        called["args"] = (provider, api_key)

    monkeypatch.setattr(set_cli, "store_credentials", fake_store_credentials)

    result = runner.invoke(set_cli.app, ["auth", "qobuz"], input="secret\n")

    assert result.exit_code == 0
    assert called["args"] == ("qobuz", "secret")
    assert "API key" in result.stdout
    assert "Credentials saved." in result.stdout


def test_path_saves_paths(monkeypatch, tmp_path):
    called = {}

    def fake_save_paths(library, cache):
        called["args"] = (library, cache)
        return {"library": library, "cache": cache}

    monkeypatch.setattr(set_cli, "save_paths", fake_save_paths)

    lib = tmp_path / "lib"
    cache = tmp_path / "cache"

    result = runner.invoke(
        set_cli.app,
        ["path", "--library", str(lib), "--cache", str(cache)],
    )

    assert result.exit_code == 0
    assert called["args"] == (lib, cache)
    assert str({"library": lib, "cache": cache}) in result.stdout


def test_path_saves_defaults(monkeypatch):
    called = {}

    def fake_save_paths(library, cache):
        called["args"] = (library, cache)
        return {"library": library, "cache": cache}

    monkeypatch.setattr(set_cli, "save_paths", fake_save_paths)

    result = runner.invoke(set_cli.app, ["path"])

    assert result.exit_code == 0
    assert called["args"] == (None, None)
    assert str({"library": None, "cache": None}) in result.stdout
