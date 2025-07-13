"""Unit tests for the ``flaccid get`` CLI wrapper."""

from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def test_get_fails_without_args():
    result = runner.invoke(app, ["get"])
    assert result.exit_code != 0
