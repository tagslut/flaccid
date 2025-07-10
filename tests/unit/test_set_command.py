from typer.testing import CliRunner

from fla.__main__ import app
from flaccid.set import cli as set_cli

runner = CliRunner()


def test_root_set_auth(monkeypatch):
    called = {}

    def fake_store(provider: str, api_key: str) -> None:
        called["args"] = (provider, api_key)

    monkeypatch.setattr(set_cli, "store_credentials", fake_store)

    result = runner.invoke(app, ["set", "auth", "qobuz"], input="secret\n")

    assert result.exit_code == 0
    assert called["args"] == ("qobuz", "secret")
