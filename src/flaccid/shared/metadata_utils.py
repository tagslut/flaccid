"""
✅ FLACCID Development Session Summary
Date: July 9, 2025
Scope: Metadata enrichment pipeline implementation and plugin verification

🧱 Metadata Fields Confirmed

You finalized the UCP (Unified Canonical Payload) structure for track metadata, including:

Core fields: title, artist, album, date, tracknumber, discnumber, duration
Source-specific IDs: qobuz_id, apple_id, tidal_id, spotify_id, musicbrainz_id
Identifiers: isrc, album_upc, explicit, genre
Lyrics: lyrics.synced, lyrics.unsynced
Source structure: sources.primary, sources.fallbacks

🎧 Tagging Module Implementations

You approved and initiated integration of the following sources:

Source	API Module	Tag Module	Status
Qobuz	qobuz_api.py	qobuz.py	✅ Complete
Apple Music	apple_api.py	apple.py	✅ Complete
Spotify	spotify_api.py	tag/spotify.py	🔄 Approved for implementation
Beatport	beatport_api.py	tag/beatport.py	✅ Approved — missing from tree
Discogs	discogs_api.py	tag/discogs.py	🔄 Approved — next in queue
MusicBrainz	musicbrainz_api.py	tag/musicbrainz.py	✅ Implemented
AcoustID	acoustid_api.py	—	⏳ Awaiting implementation

You also confirmed your Discogs token and AcoustID API key are active and stored for use.

🧪 Tag Filename Template Debugging

You reviewed and confirmed the Picard-style naming logic:

Prioritizes %date%, %originalyear%, then %originaldate%, defaulting to XXXX
Applies safe replacements (: → ꞉)
You clarified that Picard does not recognize Apple-style date tags like Date unless mapped explicitly.

🧩 Git Tree Auditing

You ran tree -L 3 and confirmed several tag/ and shared/ files are missing from disk despite being approved:

Files like shared/beatport_api.py, tag/beatport.py, etc., were never saved to your filesystem.
You requested a Copilot-compatible prompt to regenerate all missing modules, which has been delivered and tailored to FLACCID’s architecture.

🔧 Next Actions

You requested:

✅ Verification of all modules implemented
✅ Copilot prompt to rebuild any missing files
⏳ Continue with discogs next
⏳ Implement acoustid_api.py with fpcalc fingerprint support
"""

from pathlib import Path
from mutagen.flac import FLAC
from typing import Dict, Optional


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
            "title": (audio.get("TITLE") or [""])[0],
            "artist": (audio.get("ARTIST") or [""])[0],
            "album": (audio.get("ALBUM") or [""])[0],
            "albumartist": (audio.get("ALBUMARTIST") or [""])[0],
            "isrc": extract_isrc_from_flac(flac_path) or "",
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
    return path.exists() and path.suffix.lower() == ".flac"


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
