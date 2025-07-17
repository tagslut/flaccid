from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def test_validate_ok(tmp_path):
    plugin = tmp_path / "p.py"
    plugin.write_text(
        """
from flaccid.plugins.base import MetadataProviderPlugin, TrackMetadata, AlbumMetadata

class Good(MetadataProviderPlugin):
    async def open(self) -> None:
        pass
    async def close(self) -> None:
        pass
    async def authenticate(self) -> None:
        pass
    async def search_track(self, query: str):
        return {}
    async def get_track(self, track_id: str) -> TrackMetadata:
        return TrackMetadata(title='t', artist='a', album='b', track_number=1, disc_number=1)
    async def get_album(self, album_id: str) -> AlbumMetadata:
        return AlbumMetadata(title='a', artist='b')
"""
    )

    result = runner.invoke(app, ["plugins", "validate", str(plugin)])
    assert result.exit_code == 0
    assert "Good: OK" in result.stdout


def test_validate_missing(tmp_path):
    plugin = tmp_path / "bad.py"
    plugin.write_text(
        """
from flaccid.plugins.base import MetadataProviderPlugin

class Bad(MetadataProviderPlugin):
    async def open(self) -> None:
        pass
    async def close(self) -> None:
        pass
    async def authenticate(self) -> None:
        pass
"""
    )

    result = runner.invoke(app, ["plugins", "validate", str(plugin)])
    assert result.exit_code != 0
    assert "missing get_album" in result.stderr

