# SPDX-License-Identifier: GPL-2.0-or-later
"""Services for interacting with audio files and metadata."""
from __future__ import annotations

from typing import Optional

from mutagen._util import MutagenError  # Updated import
from mutagen.flac import FLAC

from flaccid.core.models import AudioFile, Metadata


class Tagger:
    """A service for reading and writing metadata tags to audio files."""

    def read_tags(self, audio_file: AudioFile) -> Optional[Metadata]:
        """Read metadata tags from a FLAC file."""
        try:
            mutagen_file = FLAC(audio_file.file_path)
            if mutagen_file.tags is None:
                return None

            tags = mutagen_file.tags

            return Metadata(
                title=tags.get("title", [""])[0],
                artist=tags.get("artist", [""])[0],
                album=tags.get("album", [""])[0],
                year=tags.get("date", [None])[0],
                track_number=tags.get("tracknumber", [None])[0],
                total_tracks=tags.get("tracktotal", [None])[0],
                genre=tags.get("genre", [None])[0],
                comment=tags.get("comment", [None])[0],
            )
        except (MutagenError, IOError, KeyError):
            return None

    def write_tags(self, audio_file: AudioFile, metadata: Metadata) -> bool:
        """Write metadata tags to a FLAC file."""
        try:
            mutagen_file = FLAC(audio_file.file_path)

            if mutagen_file.tags is None:
                mutagen_file.add_tags()

            tags = mutagen_file.tags
            if tags is None:
                return False  # Should not happen after add_tags()

            tags.clear()

            tags["title"] = metadata.title
            tags["artist"] = metadata.artist
            tags["album"] = metadata.album
            if metadata.year:
                tags["date"] = metadata.year
            if metadata.track_number:
                tags["tracknumber"] = metadata.track_number
            if metadata.total_tracks:
                tags["tracktotal"] = metadata.total_tracks
            if metadata.genre:
                tags["genre"] = metadata.genre
            if metadata.comment:
                tags["comment"] = metadata.comment

            mutagen_file.save()
            return True
        except (MutagenError, IOError):
            return False
