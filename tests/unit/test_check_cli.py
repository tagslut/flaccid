from pathlib import Path
from typer.testing import CliRunner

from fla.__main__ import app

runner = CliRunner()


def test_check_success(tmp_path, monkeypatch):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin = plugin_dir / "p.py"
    plugin.write_text(
        """
from flaccid.plugins.base import MetadataProviderPlugin, TrackMetadata

class P(MetadataProviderPlugin):
    async def open(self) -> None: pass
    async def close(self) -> None: pass
    async def authenticate(self) -> None: pass
    async def search_track(self, query: str): return {}
    async def get_track(self, track_id: str) -> TrackMetadata: return TrackMetadata(title='t', artist='a', album='b', track_number=1, disc_number=1)
    async def get_album(self, album_id: str): return None
"""
    )
    monkeypatch.setenv("FLACCID_PLUGIN_PATH", str(plugin_dir))
    monkeypatch.setenv("QOBUZ_APP_ID", "id")
    monkeypatch.setenv("QOBUZ_TOKEN", "tok")
    monkeypatch.setenv("APPLE_TOKEN", "a")
    monkeypatch.setenv("DISCOGS_TOKEN", "d")
    monkeypatch.setenv("BEATPORT_TOKEN", "b")
    monkeypatch.setenv("TIDAL_TOKEN", "t")
    cfg_dir = tmp_path / ".flaccid"
    cfg_dir.mkdir()
    (cfg_dir / "paths.json").write_text('{"library": "%s", "cache": "%s"}' % (tmp_path, tmp_path))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "All checks passed" in result.stdout


def test_check_reports_issues(tmp_path, monkeypatch):
    monkeypatch.setenv("FLACCID_PLUGIN_PATH", str(tmp_path / "missing"))
    monkeypatch.delenv("QOBUZ_APP_ID", raising=False)
    monkeypatch.delenv("QOBUZ_TOKEN", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = runner.invoke(app, ["check"])
    assert result.exit_code != 0
    assert "Plugin issues" in result.stdout
    assert "Token issues" in result.stdout
    assert "Paths configuration" in result.stdout

