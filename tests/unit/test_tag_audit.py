from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from flaccid.commands.tag import app as tag_app


runner = CliRunner()


def test_audit_no_data(tmp_path: Path) -> None:
    flac = tmp_path / "song.flac"
    flac.write_text("d")
    result = runner.invoke(tag_app, ["audit", str(flac)])
    assert result.exit_code != 0
    assert "No provenance data" in result.output


def test_audit_outputs_table(tmp_path: Path) -> None:
    flac = tmp_path / "song.flac"
    flac.write_text("d")
    data = {"title": "apple"}
    flac.with_suffix(".sources.json").write_text(json.dumps(data))
    result = runner.invoke(tag_app, ["audit", str(flac)])
    assert result.exit_code == 0
    assert "title" in result.output
    assert "apple" in result.output

