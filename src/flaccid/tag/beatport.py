from flaccid.shared import beatport_api
from flaccid.shared.metadata_utils import normalize_artist

def extract_ucp_metadata(track_json):
    title = track_json.get("name")
    artist = ", ".join([a["name"] for a in track_json.get("artists", [])])
    album = track_json.get("release", {}).get("name")
    albumartist = ", ".join([a["name"] for a in track_json.get("release", {}).get("artists", [])])
    date = track_json.get("release", {}).get("release_date", "")[:10]
    tracknumber = track_json.get("track_number", 0)
    discnumber = 1  # Beatport doesn’t provide disc info
    duration = track_json.get("duration_ms", 0) / 1000.0
    isrc = track_json.get("isrc")
    genre = track_json.get("genre", {}).get("name")
    explicit = False  # Beatport does not provide this field
    beatport_id = str(track_json.get("id"))
    album_upc = track_json.get("release", {}).get("upc")
    cover = track_json.get("images", {}).get("large", {}).get("url")

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
        "explicit": explicit,
        "genre": genre,
        "beatport_id": beatport_id,
        "album_upc": album_upc,
        "lyrics": {
            "synced": "",
            "unsynced": ""
        },
        "sources": {
            "primary": "beatport",
            "fallbacks": []
        },
        "cover_art_url": cover
    }

def tag_from_beatport_id(track_id: str) -> dict:
    track = beatport_api.get_track(track_id)
    return extract_ucp_metadata(track)

def search_and_tag(query: str) -> dict:
    results = beatport_api.search_track(query)
    tracks = results.get("tracks", {}).get("items", [])
    if not tracks:
        raise ValueError("No results found for query: " + query)
    return extract_ucp_metadata(tracks[0])
