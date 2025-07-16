import pytest
from typer.testing import CliRunner

from fla.__main__ import app

from flaccid.plugins.base import TrackMetadata


@pytest.fixture
def flac_path(tmp_path):
    return tmp_path / "song.flac"


def test_download_then_tag_success(monkeypatch, flac_path):
    calls = {}

    def fake_download(track_id: str, dest):
        calls['download'] = track_id
        dest.write_text('audio')
        return True

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_track(self, track_id: str):
            calls['track'] = track_id
            return TrackMetadata(
                title='t',
                artist='a',
                album='b',
                track_number=1,
                disc_number=1,
            )

    async def fake_fetch_and_tag(file, data, *, filename_template=None):
        calls['tag'] = file

    monkeypatch.setattr('flaccid.commands.get.qobuz_download', fake_download)
    monkeypatch.setattr('flaccid.commands.tag.AppleMusicPlugin', lambda: FakePlugin())
    monkeypatch.setattr('flaccid.commands.tag.fetch_and_tag', fake_fetch_and_tag)

    runner = CliRunner()
    result_dl = runner.invoke(app, ['download', 'qobuz', '123', str(flac_path)])
    assert result_dl.exit_code == 0
    assert flac_path.exists()

    result_tag = runner.invoke(app, ['meta', 'apple', str(flac_path), '--track-id', '999'])
    assert result_tag.exit_code == 0
    assert calls['download'] == '123'
    assert calls['track'] == '999'
    assert calls['tag'] == flac_path


def test_download_then_tag_failure(monkeypatch, flac_path):
    def fake_download(track_id: str, dest):
        dest.write_text('audio')
        return True

    class FakePlugin:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_track(self, track_id: str):
            raise ValueError('not found')

    monkeypatch.setattr('flaccid.commands.get.qobuz_download', fake_download)
    monkeypatch.setattr('flaccid.commands.tag.AppleMusicPlugin', lambda: FakePlugin())

    runner = CliRunner()
    result_dl = runner.invoke(app, ['download', 'qobuz', '123', str(flac_path)])
    assert result_dl.exit_code == 0
    assert flac_path.exists()

    result_tag = runner.invoke(app, ['meta', 'apple', str(flac_path), '--track-id', '999'])
    assert result_tag.exit_code != 0
