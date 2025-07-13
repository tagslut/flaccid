from typer.testing import CliRunner

from fla.__main__ import app
from flaccid.commands import settings as settings_cli

runner = CliRunner()


def test_root_set_auth(monkeypatch):
    called = {}

    def fake_store(realm: str, service: str, token: str) -> None:
        called["args"] = (realm, service, token)

    monkeypatch.setattr(settings_cli.keyring, "set_password", fake_store)

    result = runner.invoke(app, ["settings", "store", "qobuz"], input="secret\n")

    assert result.exit_code == 0
    assert called["args"] == ("flaccid", "qobuz", "secret")
