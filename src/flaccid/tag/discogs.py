from shared.discogs_api import get_release

def get_metadata(release_id: str) -> dict:
    data = get_release(release_id)
    artists = ", ".join([a.get("name", "") for a in data.get("artists", [])]).strip()
    albumartist = artists
    return {
        "title": data.get("title", "").strip(),
        "artist": artists,
        "album": data.get("title", "").strip(),
        "albumartist": albumartist,
        "label": ", ".join([l.get("name", "") for l in data.get("labels", [])]),
        "catalog_number": ", ".join([l.get("catno", "") for l in data.get("labels", [])]),
        "genre": ", ".join(data.get("genres", [])),
        "date": data.get("released", ""),
        "discogs_id": data.get("id", ""),
        "cover_art_url": data.get("images", [{}])[0].get("uri", "") if data.get("images") else "",
        "sources": {"primary": "discogs", "fallbacks": []},
    }
