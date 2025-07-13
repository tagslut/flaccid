"""Unit tests for the ``flaccid tag`` command group."""

from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def get_output(result):
    try:
        return result.stderr
    except Exception:
        return result.output


def test_meta_requires_subcommand():
    result = runner.invoke(app, ["meta"])
    assert result.exit_code != 0


def test_meta_errors_on_missing_path(tmp_path):
    missing = tmp_path / "nope.flac"
    result = runner.invoke(app, ["meta", "apple", str(missing), "123"])
    assert result.exit_code != 0
