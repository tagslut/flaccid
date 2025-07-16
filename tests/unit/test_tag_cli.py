"""Unit tests for the ``flaccid tag`` CLI utilities."""

import json

from typer.testing import CliRunner

import flaccid.tag.cli as tag_cli
from flaccid.tag.cli import app as tag_app

runner = CliRunner()


def test_fetch_invokes_provider(tmp_path, monkeypatch):
    called = {}

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def search_track(self, query: str):
            called["query"] = query
            return {"ok": True}

    monkeypatch.setattr(tag_cli, "get_provider", lambda name: FakePlugin)
    monkeypatch.setattr(tag_cli, "get_existing_metadata", lambda path: {})
    monkeypatch.setattr(tag_cli, "build_search_query", lambda meta: "A B")

    flac = tmp_path / "song.flac"
    flac.write_text("data")

    result = runner.invoke(tag_app, ["fetch", str(flac)])

    assert result.exit_code == 0
    assert called["query"] == "A B"
    assert "{'ok': True}" in result.stdout


def test_apply_invokes_helper(tmp_path, monkeypatch):
    called = {}

    def fake_apply_metadata(file, metadata_file, yes):
        called["args"] = (file, metadata_file, yes)

    monkeypatch.setattr(tag_cli.utils, "apply_metadata", fake_apply_metadata)

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


async def fake_write_tags(*args, **kwargs):
    return args[0]  # or a Path object as needed


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

    called = {"write": []}  # Initialize the dictionary with the 'write' key

    def mock_write_tags(file, metadata):
        called["write"].append(file)
        return True

    class FakeLyrics:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_lyrics(self, artist: str, title: str):
            return "la"

    import flaccid.tag.utils as tag_utils

    monkeypatch.setattr(tag_utils, "write_tags", fake_write_tags)
    monkeypatch.setattr(tag_utils, "LyricsPlugin", lambda: FakeLyrics())
    monkeypatch.setattr(tag_utils, "confirm", lambda m: True)
    monkeypatch.setattr("flaccid.tag.write_tags", mock_write_tags)

    result = runner.invoke(tag_app, ["apply", str(flac), "--metadata-file", str(meta)])

    assert result.exit_code == 0
    assert called["write"] == [flac]


def test_apple_template_option(tmp_path, monkeypatch):
    """``apple`` should forward ``--template`` to ``fetch_and_tag``."""

    import flaccid.commands.tag as commands_tag

    captured: dict[str, object] = {}

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_track(self, track_id: str):
            captured["track_id"] = track_id
            return {"meta": True}

    async def fake_fetch_and_tag(file, data, *, filename_template=None):
        captured["template"] = filename_template
        captured["file"] = file

    monkeypatch.setattr(commands_tag, "AppleMusicPlugin", lambda: FakePlugin())
    monkeypatch.setattr(commands_tag, "fetch_and_tag", fake_fetch_and_tag)

    flac = tmp_path / "song.flac"
    flac.write_text("data")

    runner = CliRunner()
    result = runner.invoke(
        commands_tag.app,
        [
            "apple",
            str(flac),
            "--track-id",
            "123",
            "--template",
            "{artist}-{title}.flac",
        ],
    )

    assert result.exit_code == 0
    assert captured["template"] == "{artist}-{title}.flac"
