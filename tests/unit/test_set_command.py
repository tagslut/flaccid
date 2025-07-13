from typer.testing import CliRunner

from fla.__main__ import app
from flaccid.set import cli as set_cli

runner = CliRunner()


def test_root_set_auth(monkeypatch):
    called = {}

    def fake_set_password(service: str, provider: str, token: str) -> None:
        called["args"] = (service, provider, token)

    monkeypatch.setattr(set_cli.keyring, "set_password", fake_set_password)

    result = runner.invoke(app, ["set", "auth", "qobuz"], input="secret\n")

    assert result.exit_code == 0
    assert called["args"] == ("flaccid", "qobuz", "secret")
