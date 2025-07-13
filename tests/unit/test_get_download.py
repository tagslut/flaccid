from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def get_output(result):
    try:
        return result.stderr
    except Exception:
        return result.output


def test_download_requires_subcommand():
    result = runner.invoke(app, ["download"])
    assert result.exit_code != 0


def test_download_unknown_service_errors():
    result = runner.invoke(app, ["download", "not-a-service"])
    assert result.exit_code != 0
