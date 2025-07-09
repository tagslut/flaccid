from shared.beatport_api import get_track

def get_metadata(track_id: str) -> dict:
    data = get_track(track_id)
    track = data if isinstance(data, dict) else {}
    artists = ", ".join([a.get("name", "") for a in track.get("artists", [])]).strip()
    album = track.get("release", {}).get("name", "")
    albumartist = ", ".join([a.get("name", "") for a in track.get("release", {}).get("artists", [])]).strip()
    return {
        "title": track.get("name", "").strip(),
        "artist": artists,
        "album": album.strip(),
        "albumartist": albumartist,
        "tracknumber": str(track.get("number", "")),
        "duration": int(track.get("duration", 0)) // 1000,
        "date": track.get("release", {}).get("release_date", "")[:10],
        "label": track.get("release", {}).get("label", {}).get("name", ""),
        "catalog_number": track.get("release", {}).get("catalog_number", ""),
        "genre": ", ".join([g.get("name", "") for g in track.get("genres", [])]),
        "isrc": track.get("isrc", ""),
        "cover_art_url": track.get("image", {}).get("uri", ""),
        "beatport_id": track.get("id", ""),
        "sources": {"primary": "beatport", "fallbacks": []},
    }
