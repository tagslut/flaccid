import os

import pytest
from typer.testing import CliRunner

from flaccid.cli import app

runner = CliRunner()


@pytest.fixture
def mock_env():
    os.environ["APPLE_MUSIC_API_KEY"] = "mock_api_key"
    yield
    del os.environ["APPLE_MUSIC_API_KEY"]


def test_apple_help():
    result = runner.invoke(app, ["apple", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--auth" in result.output
    assert "--status" in result.output


def test_apple_auth_and_status(mock_env):
    res_auth = runner.invoke(app, ["apple", "--auth"])
    assert res_auth.exit_code == 0
    assert "Authenticated" in res_auth.output

    res_status = runner.invoke(app, ["apple", "--status"])
    assert res_status.exit_code == 0
    assert "Authenticated" in res_status.output
