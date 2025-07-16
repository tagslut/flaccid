"""Unit tests for the ``flaccid set`` CLI group."""

from typer.testing import CliRunner

from flaccid.set.cli import app as set_app
import flaccid.set.cli as set_cli


runner = CliRunner()


def test_auth_prompts_for_key_and_secret(monkeypatch):
    """Ensure both API key and secret are requested and stored."""

    called = {}

    def fake_store(provider: str, key: str, secret: str) -> None:
        called["args"] = (provider, key, secret)

    monkeypatch.setattr(set_cli, "store_credentials", fake_store)

    result = runner.invoke(set_app, ["auth", "qobuz"], input="k\ns\n")

    assert result.exit_code == 0
    assert called["args"] == ("qobuz", "k", "s")
    assert "Credentials saved." in result.stdout
