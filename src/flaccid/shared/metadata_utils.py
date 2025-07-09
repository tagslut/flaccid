from pathlib import Path
from mutagen.flac import FLAC
from typing import Dict, Optional
import re  # NEW

def extract_isrc_from_flac(flac_path: str) -> Optional[str]:
    """Extract ISRC from FLAC file if available."""
    try:
        audio = FLAC(flac_path)
        # Common ISRC tag names
        isrc_tags = ["ISRC", "isrc", "TSRC"]

        for tag in isrc_tags:
            if tag in audio:
                return audio[tag][0]

        return None
    except Exception:
        return None

def get_existing_metadata(flac_path: str) -> Dict[str, str]:
    """Get existing metadata from FLAC file for search queries."""
    try:
        audio = FLAC(flac_path)
        return {
            "title": audio.get("TITLE", [""])[0],
            "artist": audio.get("ARTIST", [""])[0],
            "album": audio.get("ALBUM", [""])[0],
            "albumartist": audio.get("ALBUMARTIST", [""])[0],
            "isrc": extract_isrc_from_flac(flac_path)
        }
    except Exception:
        return {}

def build_search_query(metadata: Dict[str, str]) -> str:
    """Build search query from existing metadata."""
    title = metadata.get("title", "")
    artist = metadata.get("artist", "")

    if title and artist:
        return f"{artist} {title}"
    elif title:
        return title
    elif artist:
        return artist
    else:
        return ""

def validate_flac_file(file_path: str) -> bool:
    """Validate that file exists and is a FLAC file."""
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == '.flac'

def apply_metadata_to_flac(flac_path: str, metadata: Dict[str, str]) -> bool:
    """Apply metadata dictionary to FLAC file."""
    try:
        audio = FLAC(flac_path)

        # Apply all metadata
        for key, value in metadata.items():
            if value:  # Only set non-empty values
                audio[key.upper()] = value

        audio.save()
        return True
    except Exception:
        return False

def normalize_artist(name: str | None) -> str | None:
    """
    Basic artist-name cleanup:
    • Trim leading/trailing whitespace
    • Collapse multiple consecutive spaces to one
    Keeps original casing.
    """
    if not name:
        return name
    return re.sub(r"\s{2,}", " ", name.strip())
