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


def test_qobuz_download_success(monkeypatch, tmp_path):
    called: dict[str, object] = {}

    def fake_download(track_id: str, dest):
        called["args"] = (track_id, dest)
        dest.write_text("data")
        return True

    import flaccid.commands.get as get_cli

    monkeypatch.setattr(get_cli, "qobuz_download", fake_download)

    out = tmp_path / "file.flac"
    result = runner.invoke(app, ["download", "qobuz", "123", str(out)])

    assert result.exit_code == 0
    assert called["args"] == ("123", out)
    assert f"Saved to {out}" in result.stdout


def test_qobuz_download_failure(monkeypatch, tmp_path):
    def fake_download(track_id: str, dest):
        return False

    import flaccid.commands.get as get_cli

    monkeypatch.setattr(get_cli, "qobuz_download", fake_download)

    out = tmp_path / "file.flac"
    result = runner.invoke(app, ["download", "qobuz", "123", str(out)])

    assert result.exit_code != 0
    assert "Download failed" in result.stderr
