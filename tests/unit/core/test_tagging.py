# SPDX-License-Identifier: GPL-2.0-or-later
from pathlib import Path
from flaccid.core import tagging

SAMPLE = (
    Path(__file__).parent.parent.parent
    / "fixtures"
    / "Pixies - (1988) Surfer Rosa (2007 Remaster) - 07. Where Is My Mind?.flac"
)


def test_read_tags_has_title():
    tags = tagging.read_tags(SAMPLE)
    assert tags["title"].lower() == "where is my mind?"


def test_write_and_rename(tmp_path):
    test_copy = tmp_path / "track.flac"
    test_copy.write_bytes(SAMPLE.read_bytes())

    tagging.write_tags(test_copy, {"title": "Tmp"})
    assert tagging.read_tags(test_copy)["title"] == "Tmp"

    new_path = tagging.rename_file(test_copy, "%{title}")
    assert new_path.name == "Tmp.flac"
