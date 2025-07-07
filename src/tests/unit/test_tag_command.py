from typer.testing import CliRunner
from fla.__main__ import app

runner = CliRunner()


def test_tag_fails_without_args():
    result = runner.invoke(app, ["tag"])
    assert result.exit_code != 0
