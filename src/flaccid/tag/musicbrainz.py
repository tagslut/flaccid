from shared.musicbrainz_api import get_recording

def get_metadata(recording_id: str) -> dict:
    data = get_recording(recording_id)
    artist = ", ".join([a.get("name", "") for a in data.get("artist-credit", []) if a.get("name")])
    album = data.get("releases", [{}])[0].get("title", "") if data.get("releases") else ""
    albumartist = artist
    return {
        "title": data.get("title", "").strip(),
        "artist": artist,
        "album": album,
        "albumartist": albumartist,
        "tracknumber": str(data.get("position", "")),
        "discnumber": str(data.get("discnumber", "")),
        "duration": int(data.get("length", 0)) // 1000,
        "isrc": ", ".join(data.get("isrcs", [])),
        "musicbrainz_id": data.get("id", ""),
        "date": data.get("first-release-date", ""),
        "genre": ", ".join([t.get("name", "") for t in data.get("tags", [])]),
        "sources": {"primary": "musicbrainz", "fallbacks": []},
    }
