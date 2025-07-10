from pathlib import Path

from flaccid.core import library


def test_scan_directory(tmp_path: Path):
    flac = tmp_path / "test.flac"
    flac.write_bytes(b"\x00\x00")
    other = tmp_path / "skip.mp3"
    other.write_text("nope")

    files = library.scan_directory(tmp_path)
    assert flac in files
    assert other not in files
