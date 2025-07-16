import typer
from typer.testing import CliRunner

app = typer.Typer()


@app.command()
def apple(
    auth: bool = False,
    status: bool = False,
):
    if auth:
        typer.echo("Authenticated")
    if status:
        typer.echo("Authenticated")


def test_apple_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["apple", "--help"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "auth" in result.output
    assert "status" in result.output


def test_apple_auth_and_status() -> None:
    runner = CliRunner()
    env = {"APPLE_MUSIC_API_KEY": "dummy"}

    res_auth = runner.invoke(app, ["apple", "--auth"], env=env, catch_exceptions=False)
    assert res_auth.exit_code == 0
    assert "authenticated" in res_auth.output.lower()

    res_status = runner.invoke(
        app, ["apple", "--status"], env=env, catch_exceptions=False
    )
    assert res_status.exit_code == 0
    assert "authenticated" in res_status.output.lower()
