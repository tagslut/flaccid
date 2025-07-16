from typer.testing import CliRunner

import flaccid.set.cli as set_cli
from flaccid.set.cli import app as set_app

runner = CliRunner()


def test_auth_prompts_and_stores(monkeypatch):
    calls = {}

    def fake_store(provider: str, key: str, secret: str) -> None:
        calls["args"] = (provider, key, secret)

    monkeypatch.setattr(set_cli, "store_credentials", fake_store)

    result = runner.invoke(set_app, ["auth", "qobuz"], input="key\nsecret\n")

    assert result.exit_code == 0
    assert calls["args"] == ("qobuz", "key", "secret")
    assert "Credentials saved." in result.stdout
