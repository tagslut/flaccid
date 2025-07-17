"""Unit tests for the ``flaccid tag`` CLI utilities."""

import json

from typer.testing import CliRunner
from flaccid.plugins.base import TrackMetadata

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
    monkeypatch.setattr(tag_cli.utils, "get_provider", lambda name: FakePlugin)
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

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def search_track(self, query: str):  # pragma: no cover - not used
            return TrackMetadata(
                title="T",
                artist="A",
                album="B",
                track_number=1,
                disc_number=1,
            )

    def fake_apply_metadata(file, meta, yes, export_lrc):
        called["args"] = (file, meta, yes, export_lrc)

    monkeypatch.setattr(tag_cli.utils, "apply_metadata", fake_apply_metadata)
    monkeypatch.setattr(tag_cli.utils, "get_provider", lambda name: FakePlugin)
    monkeypatch.setattr(
        tag_cli.utils,
        "get_existing_metadata",
        lambda p: {"artist": "Artist", "title": "Song"},
    )
    monkeypatch.setattr(
        tag_cli.utils,
        "build_search_query",
        lambda m: "Artist Song",
    )

    flac = tmp_path / "song.flac"
    flac.write_text("data")
    metadata = tmp_path / "meta.json"
    metadata.write_text("{}")

    result = runner.invoke(
        tag_app, ["apply", str(flac), "--metadata-file", str(metadata), "--yes"]
    )

    assert result.exit_code == 0
    assert called["args"][0] == flac
    assert isinstance(called["args"][1], TrackMetadata)
    assert called["args"][2] is True
    assert called["args"][3] is False
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
    monkeypatch.setattr("flaccid.core.metadata.write_tags", mock_write_tags)

    result = runner.invoke(tag_app, ["apply", str(flac), "--metadata-file", str(meta)])

    assert result.exit_code == 0
    assert called["write"] == [flac]


def test_apply_no_metadata_fetches(tmp_path, monkeypatch):
    called: dict[str, object] = {}

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def search_track(self, query: str):
            called["query"] = query
            return TrackMetadata(
                title="Song",
                artist="Artist",
                album="A",
                track_number=1,
                disc_number=1,
            )

    def fake_apply_metadata(file, meta, yes, export_lrc):
        called["apply"] = (file, meta, yes, export_lrc)

    monkeypatch.setattr(tag_cli, "get_provider", lambda name: FakePlugin)
    monkeypatch.setattr(tag_cli.utils, "get_provider", lambda name: FakePlugin)
    monkeypatch.setattr(
        tag_cli,
        "get_existing_metadata",
        lambda path: {"artist": "Artist", "title": "Song"},
    )
    monkeypatch.setattr(tag_cli, "build_search_query", lambda meta: "Artist Song")
    monkeypatch.setattr(tag_cli.utils, "apply_metadata", fake_apply_metadata)

    flac = tmp_path / "song.flac"
    flac.write_text("data")

    result = runner.invoke(tag_app, ["apply", str(flac), "--yes"])

    assert result.exit_code == 0
    assert called["apply"][0] == flac
    assert isinstance(called["apply"][1], TrackMetadata)
    assert called["apply"][2] is True
    assert called["apply"][3] is False


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

    async def fake_fetch_and_tag(
        file,
        data,
        *,
        strategies=None,
        filename_template=None,
    ):
        captured["template"] = filename_template
        captured["file"] = file
        captured["strategies"] = strategies

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
            "--strategy.title",
            "replace",
        ],
    )

    assert result.exit_code == 0
    assert captured["template"] == "{artist}-{title}.flac"
    assert captured["strategies"] == {"title": "replace"}


def test_review_command(tmp_path, monkeypatch):
    import flaccid.commands.tag as commands_tag

    flac = tmp_path / "track.flac"
    flac.write_text("data")

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def search_track(self, query: str):
            return TrackMetadata(
                title="T",
                artist="A",
                album="B",
                track_number=1,
                disc_number=1,
            )

    reviewed = TrackMetadata(
        title="T",
        artist="A",
        album="B",
        track_number=1,
        disc_number=1,
    )

    def fake_apply(file, meta, yes, export_lrc):
        fake_apply.called = (file, meta, yes, export_lrc)

    monkeypatch.setattr(commands_tag, "get_provider", lambda name: FakePlugin)
    monkeypatch.setattr(commands_tag, "get_existing_metadata", lambda p: {})
    monkeypatch.setattr(commands_tag, "build_search_query", lambda m: "Q")
    monkeypatch.setattr(commands_tag.utils, "apply_metadata", fake_apply)
    monkeypatch.setattr("flaccid.tui.review.review_metadata", lambda m: reviewed)
    monkeypatch.setattr("keyring.get_password", lambda *a, **k: None)
    monkeypatch.setattr("keyring.set_password", lambda *a, **k: None)

    result = runner.invoke(commands_tag.app, ["review", str(flac)])

    assert result.exit_code == 0
    assert fake_apply.called[0] == flac
    assert fake_apply.called[1] == reviewed
    assert fake_apply.called[2] is True
