"""
MusicBrainz tag integration for FLACCID.

Normalises MusicBrainz recording metadata into the Unified Canonical
Payload (UCP) format used by the rest of the tagging pipeline.
"""

from flaccid.shared import musicbrainz_api
from flaccid.shared.metadata_utils import normalize_artist

__all__ = ["get_metadata", "search_and_tag"]


def _extract_ucp(recording: dict) -> dict:
    """Convert a MusicBrainz recording JSON into UCP-style metadata."""
    release = recording.get("releases", [{}])[0]
    artists = recording.get("artist-credit", [])

    title = recording.get("title")
    artist = ", ".join(a.get("name") for a in artists if "name" in a)

    album = release.get("title")
    album_artists = release.get("artist-credit", [])
    albumartist = (
        ", ".join(a.get("name") for a in album_artists) if album_artists else artist
    )

    tracknumber = release.get("track-number")
    discnumber = release.get("disc-number")
    duration = (recording.get("length") or 0) / 1000  # → seconds

    isrcs = recording.get("isrcs", [])
    isrc = isrcs[0] if isrcs else None
    date = (release.get("date") or "")[:10]

    return {
        "title": title,
        "artist": normalize_artist(artist),
        "album": album,
        "albumartist": normalize_artist(albumartist),
        "date": date,
        "tracknumber": tracknumber,
        "discnumber": discnumber,
        "duration": duration,
        "isrc": isrc,
        "musicbrainz_id": recording.get("id"),
        "lyrics": {"synced": "", "unsynced": ""},
        "cover_art_url": None,  # Use Cover Art Archive later if needed
        "sources": {
            "primary": "musicbrainz",
            "fallbacks": [],
        },
    }


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def get_metadata(recording_id: str) -> dict:
    """Fetch a recording by MusicBrainz ID and return UCP metadata."""
    recording_json = musicbrainz_api.get_recording(recording_id)
    return _extract_ucp(recording_json)


def search_and_tag(query: str) -> dict:
    """
    Search MusicBrainz for the best matching recording using a query string
    and return its UCP metadata.
    """
    results = musicbrainz_api.search_recording(query, limit=1)
    if not results:
        raise ValueError(f"No MusicBrainz result for query: {query}")
    return get_metadata(results[0]["id"])