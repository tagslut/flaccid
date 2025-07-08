from pathlib import Path
from mutagen.flac import FLAC
from typing import Dict, Optional

<<<<<<< HEAD
=======

>>>>>>> df23120cd62222d9a0cfa66459ce26f4cb473994
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

<<<<<<< HEAD
=======

>>>>>>> df23120cd62222d9a0cfa66459ce26f4cb473994
def get_existing_metadata(flac_path: str) -> Dict[str, str]:
    """Get existing metadata from FLAC file for search queries."""
    try:
        audio = FLAC(flac_path)
        return {
            "title": audio.get("TITLE", [""])[0],
            "artist": audio.get("ARTIST", [""])[0],
            "album": audio.get("ALBUM", [""])[0],
            "albumartist": audio.get("ALBUMARTIST", [""])[0],
<<<<<<< HEAD
            "isrc": extract_isrc_from_flac(flac_path)
=======
            "isrc": extract_isrc_from_flac(flac_path),
>>>>>>> df23120cd62222d9a0cfa66459ce26f4cb473994
        }
    except Exception:
        return {}

<<<<<<< HEAD
=======

>>>>>>> df23120cd62222d9a0cfa66459ce26f4cb473994
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

<<<<<<< HEAD
def validate_flac_file(file_path: str) -> bool:
    """Validate that file exists and is a FLAC file."""
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == '.flac'
=======

def validate_flac_file(file_path: str) -> bool:
    """Validate that file exists and is a FLAC file."""
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == ".flac"

>>>>>>> df23120cd62222d9a0cfa66459ce26f4cb473994

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
