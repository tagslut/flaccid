from typer.testing import CliRunner
from fla.__main__ import app
from fla.shared.qobuz_api import QobuzAPI

runner = CliRunner()


def test_lib_fails_without_args():
    result = runner.invoke(app, ["lib"])
    assert result.exit_code != 0
