"""
AcoustID tag integration for FLACCID.

Workflow
--------
1.  Generate a Chromaprint fingerprint for a local audio file.
2.  Submit the fingerprint to AcoustID using the user’s API key.
3.  Retrieve the best-match MusicBrainz recording ID.
4.  Delegate to tag.musicbrainz.get_metadata() to obtain
    full canonical metadata in UCP format.
"""

from pathlib import Path
from flaccid.shared import acoustid_api
from flaccid.tag import musicbrainz

__all__ = ["tag_file", "search_and_tag"]


def tag_file(audio_path: str | Path) -> dict:
    """
    Generate metadata for *audio_path* by fingerprinting the file.

    Returns the UCP dict produced by tag.musicbrainz.
    Raises ValueError if no confident match is found.
    """
    audio_path = Path(audio_path).expanduser().resolve()
    fp, duration = acoustid_api.generate_fingerprint(audio_path)
    result = acoustid_api.lookup_mbids(fp, duration)

    if not result or "recordings" not in result[0]:
        raise ValueError("No MusicBrainz match returned by AcoustID.")

    mbid = result[0]["recordings"][0]["id"]
    return musicbrainz.get_metadata(mbid)


def search_and_tag(query: str) -> dict:
    """
    Thin wrapper provided for API parity with other tag modules.
    AcoustID is fingerprint-based, so *query* is ignored and
    ValueError is raised.
    """
    raise ValueError(
        "AcoustID tagging requires an audio file fingerprint, "
        "not a text query. Use tag_file(<path>) instead."
    )