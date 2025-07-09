"""
Spotify tag integration for FLACCID.

Normalises Spotify track metadata into the Unified Canonical Payload (UCP)
format so other pipeline stages can write tags or filenames consistently.
"""

from flaccid.shared import spotify_api
from flaccid.shared.metadata_utils import normalize_artist

__all__ = ["get_metadata", "search_and_tag"]


# ----------------------------------------------------------------------
def _extract_ucp(track: dict) -> dict:
    """Convert a Spotify track JSON object into UCP-style metadata."""
    album = track.get("album", {})
    artists = track.get("artists", [])

    title = track.get("name")
    artist = ", ".join(a["name"] for a in artists)
    albumartist = ", ".join(a["name"] for a in album.get("artists", []))

    tracknumber = track.get("track_number")
    discnumber = track.get("disc_number")
    duration = track.get("duration_ms", 0) / 1000  # milliseconds → seconds
    isrc = track.get("external_ids", {}).get("isrc")
    release_date = (album.get("release_date") or "")[:10]  # YYYY or YYYY-MM-DD

    cover_url = None
    if album.get("images"):
        # pick the largest image
        cover_url = sorted(
            album["images"], key=lambda img: img.get("width", 0), reverse=True
        )[0]["url"]

    return {
        "title": title,
        "artist": normalize_artist(artist),
        "album": album.get("name"),
        "albumartist": normalize_artist(albumartist),
        "date": release_date,
        "tracknumber": tracknumber,
        "discnumber": discnumber,
        "duration": duration,
        "isrc": isrc,
        "explicit": track.get("explicit", False),
        "genre": None,  # Spotify API does not expose per-track genre
        "spotify_id": track.get("id"),
        "album_upc": album.get("external_ids", {}).get("upc"),
        "lyrics": {"synced": "", "unsynced": ""},
        "cover_art_url": cover_url,
        "sources": {
            "primary": "spotify",
            "fallbacks": [],
        },
    }


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def get_metadata(track_id: str) -> dict:
    """
    Retrieve a Spotify track by ID and return a UCP metadata dictionary.
    """
    track_json = spotify_api.get_track(track_id)
    return _extract_ucp(track_json)


def search_and_tag(query: str) -> dict:
    """
    Search Spotify for *query* (artist + title string) and return UCP
    metadata for the best match.
    """
    results = spotify_api.search_track(query, limit=1)
    if not results:
        raise ValueError(f"No Spotify result for query: {query}")
    return _extract_ucp(results[0])