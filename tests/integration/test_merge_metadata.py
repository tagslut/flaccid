import json
from pathlib import Path

import pytest

from flaccid.core import metadata
from flaccid.plugins.base import TrackMetadata


@pytest.mark.asyncio
async def test_fetch_and_tag_merges_partial_results(
    tmp_path: Path, monkeypatch
) -> None:
    """Metadata from three providers should merge correctly."""

    file_path = tmp_path / "song.flac"
    file_path.write_text("audio")

    captured: dict[str, TrackMetadata] = {}

    async def fake_write_tags(path: Path, meta: TrackMetadata, **kwargs) -> Path:
        captured["meta"] = meta
        return path

    monkeypatch.setattr(metadata, "write_tags", fake_write_tags)

    provider_a = TrackMetadata(
        title="Song",
        artist="",
        album="Album",
        track_number=1,
        disc_number=1,
        source="prov_a",
    )
    provider_b = TrackMetadata(
        title="",
        artist="Artist",
        album="",
        track_number=1,
        disc_number=1,
        lyrics="la",
        source="prov_b",
    )
    provider_c = TrackMetadata(
        title="",
        artist="",
        album="",
        track_number=1,
        disc_number=1,
        year=2025,
        isrc="XYZ",
        source="prov_c",
    )

    await metadata.fetch_and_tag(file_path, provider_a, provider_b, provider_c)

    merged = captured["meta"]
    assert merged.title == "Song"
    assert merged.artist == "Artist"
    assert merged.album == "Album"
    assert merged.year == 2025
    assert merged.isrc == "XYZ"
    assert merged.lyrics == "la"

    prov_file = file_path.with_suffix(".sources.json")
    with prov_file.open() as fh:
        provenance = json.load(fh)

    assert provenance["title"] == "prov_a"
    assert provenance["artist"] == "prov_b"
    assert provenance["year"] == "prov_c"
    assert provenance["isrc"] == "prov_c"
    assert provenance["lyrics"] == "prov_b"


@pytest.mark.asyncio
async def test_fetch_and_tag_respects_precedence(
    tmp_path: Path, monkeypatch
) -> None:
    """Providers listed first should take precedence when fields overlap."""

    file_path = tmp_path / "song.flac"
    file_path.write_text("audio")

    captured: dict[str, TrackMetadata] = {}

    async def fake_write_tags(path: Path, meta: TrackMetadata, **kwargs) -> Path:
        captured["meta"] = meta
        return path

    monkeypatch.setattr(metadata, "write_tags", fake_write_tags)

    provider_a = TrackMetadata(
        title="A",
        artist="",
        album="",
        track_number=1,
        disc_number=1,
        source="prov_a",
    )
    provider_b = TrackMetadata(
        title="B",
        artist="",
        album="",
        track_number=1,
        disc_number=1,
        source="prov_b",
    )

    monkeypatch.setenv("PLUGIN_PRECEDENCE", "prov_b,prov_a")
    await metadata.fetch_and_tag(file_path, provider_a, provider_b)
    assert captured["meta"].title == "B"
