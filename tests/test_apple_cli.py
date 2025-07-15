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
    assert "auth" in result.output


def test_apple_auth_and_status():
    res_auth = runner.invoke(app, ["apple", "auth", "--valid-arg"])
    assert res_auth.exit_code == 0
