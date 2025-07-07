# SPDX-License-Identifier: GPL-2.0-or-later
"""Read / write audio metadata using Mutagen and rename files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.id3._frames import TIT2
from mutagen._file import File

TAG_MAP: Dict[str, str] = {
    "title": "TITLE",
    "tracknumber": "TRACKNUMBER",
    "artist": "ARTIST",
    "album": "ALBUM",
    "date": "DATE",
}


class TaggingError(RuntimeError):
    """Raised when read/write fails."""


def read_tags(path: str | Path) -> Dict[str, Any]:
    """Return a simple dict of common tags. Unknown keys are ignored."""
    audio = _open(path)
    if audio.tags is None:
        raise TaggingError(f"No tags found in file: {path}")
    result: Dict[str, Any] = {}
    for key, muta_key in TAG_MAP.items():
        value = audio.tags.get(muta_key) if audio.tags else None
        if value:
            result[key] = value[0] if isinstance(value, list) else value
    return result


def write_tags(path: str | Path, tags: Dict[str, str]) -> None:
    """Write tags; keys must match `TAG_MAP` (title, tracknumber…)."""
    audio = _open(path)
    if audio.tags is None:
        raise TaggingError(f"No tags found in file: {path}")
    mutated = False
    for key, value in tags.items():
        muta_key = TAG_MAP.get(key.lower())
        if not muta_key:
            continue
        if isinstance(audio, FLAC):
            # FLAC tags are stored as VCFLACDict which supports assignment
            audio.tags[muta_key] = value
        elif isinstance(audio, ID3):
            if muta_key == "TITLE":
                audio.add(TIT2(encoding=3, text=value))
            else:
                # You may want to add more frame handling here for other tags
                audio[muta_key] = value  # This works for custom frames, but not all
        mutated = True
    if mutated:
        audio.save()
    else:
        raise TaggingError("No recognised tags supplied")


_PATTERN_TOKEN = re.compile(r"%\{([^}]+)}")


def rename_file(path: str | Path, pattern: str) -> Path:
    """
    Rename *path* according to pattern like:
    "[%{date}] %{album}/%{track_number} - %{title}"

    Returns the new absolute Path.
    """
    tags = read_tags(path)
    dirname = pattern
    for token in _PATTERN_TOKEN.findall(pattern):
        replacement = tags.get(token) or ""
        dirname = dirname.replace(f"%{{{token}}}", replacement)

    src = Path(path)
    dest = src.parent / dirname
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest = dest.with_suffix(src.suffix)
    src.rename(dest)
    return dest.resolve()


def _open(path: str | Path):
    audio = File(path, easy=False)
    if audio is None or audio.tags is None:
        raise TaggingError(f"Unsupported or untagged file: {path}")
    return audio
