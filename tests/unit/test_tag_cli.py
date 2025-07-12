from typer.testing import CliRunner
import json

import flaccid.tag.cli as tag_cli
from flaccid.tag.cli import app as tag_app

runner = CliRunner()


def test_fetch_invokes_placeholder(tmp_path, monkeypatch):
    called = {}

    def fake_fetch_metadata(file, provider):
        called["args"] = (file, provider)
        return {"ok": True}

    monkeypatch.setattr(tag_cli, "fetch_metadata", fake_fetch_metadata)

    flac = tmp_path / "song.flac"
    flac.write_text("data")

    result = runner.invoke(tag_app, ["fetch", str(flac)])

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
        tag_app, ["apply", str(flac), "--metadata-file", str(metadata), "--yes"]
    )

    assert result.exit_code == 0
    assert called["args"] == (flac, metadata, True)
    assert "Metadata applied successfully" in result.stdout


def test_apply_real_logic(tmp_path, monkeypatch):
    flac = tmp_path / "song.flac"
    flac.write_text("data")
    meta = tmp_path / "meta.json"
    meta.write_text(
        json.dumps(
            {
                "title": "Song",
                "artist": "Artist",
                "album": "A",
                "track_number": 1,
                "disc_number": 1,
            }
        )
    )

    called: dict[str, object] = {}

    def fake_write(path, meta_obj, art=None):
        called["write"] = path

    class FakeLyrics:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_lyrics(self, artist: str, title: str):
            return "la"

    import flaccid.cli.placeholders as placeholders

    monkeypatch.setattr(placeholders.metadata, "write_tags", fake_write)
    monkeypatch.setattr(placeholders, "LyricsPlugin", lambda: FakeLyrics())
    monkeypatch.setattr(placeholders, "confirm", lambda m: True)

    result = runner.invoke(
        tag_app, ["apply", str(flac), "--metadata-file", str(meta)]
    )

    assert result.exit_code == 0
    assert called["write"] == flac
