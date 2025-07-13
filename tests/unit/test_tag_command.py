from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def get_output(result):
    try:
        return result.stderr
    except Exception:
        return result.output


def test_tag_fails_without_path():
    result = runner.invoke(app, ["tag"])
    assert result.exit_code != 0


def test_tag_errors_on_missing_path(tmp_path):
    missing = tmp_path / "nope.flac"
    result = runner.invoke(app, ["tag", str(missing)])
    assert result.exit_code != 0
    output = get_output(result)
    assert "Path not found" in output
