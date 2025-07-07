from typer.testing import CliRunner
from fla.__main__ import app

runner = CliRunner()


def test_get_fails_without_source():
    result = runner.invoke(app, ["get"])
    assert result.exit_code != 0
    assert "Error" in result.stderr or "Missing argument" in result.stderr


def test_get_unknown_source_errors():
    result = runner.invoke(app, ["get", "not-a-source"])
    assert result.exit_code != 0
    assert "Unknown source" in result.stderr
