from typer.testing import CliRunner

from flaccid.tag import cli as tag_cli

runner = CliRunner()


def test_fetch_invokes_placeholder(tmp_path, monkeypatch):
    called = {}

    def fake_fetch_metadata(file, provider):
        called["args"] = (file, provider)
        return {"ok": True}

    monkeypatch.setattr(tag_cli, "fetch_metadata", fake_fetch_metadata)

    flac = tmp_path / "song.flac"
    flac.write_text("data")

    result = runner.invoke(tag_cli.app, ["fetch", str(flac)])

    assert result.exit_code == 0
    assert called["args"] == (flac, "qobuz")
    assert "{'ok': True}" in result.stdout


def test_apply_invokes_placeholder(tmp_path, monkeypatch):
    called = {}

    def fake_apply_metadata(file, metadata_file, yes):
        called["args"] = (file, metadata_file, yes)

    monkeypatch.setattr(tag_cli, "apply_metadata", fake_apply_metadata)

    flac = tmp_path / "song.flac"
    flac.write_text("data")
    metadata = tmp_path / "meta.json"
    metadata.write_text("{}")

    result = runner.invoke(
        tag_cli.app, ["apply", str(flac), "--metadata-file", str(metadata), "--yes"]
    )

    assert result.exit_code == 0
    assert called["args"] == (flac, metadata, True)
    assert "Metadata applied successfully" in result.stdout
