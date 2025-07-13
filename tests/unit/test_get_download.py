from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def get_output(result):
    try:
        return result.stderr
    except Exception:
        return result.output


def test_get_fails_without_source():
    result = runner.invoke(app, ["get"])
    assert result.exit_code != 0
    output = get_output(result)
    assert "Error" in output or "Missing argument" in output


def test_get_unknown_source_errors():
    result = runner.invoke(app, ["get", "not-a-source"])
    assert result.exit_code != 0
    output = get_output(result)
    assert "Unknown source" in output
