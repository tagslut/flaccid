from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def test_lib_fails_without_args():
    result = runner.invoke(app, ["lib"])
    assert result.exit_code != 0
