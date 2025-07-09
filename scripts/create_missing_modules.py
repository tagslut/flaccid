import os
from pathlib import Path

# All module files we expect to be present
MISSING_MODULES = {
    "shared/acoustid_api.py": "# TODO: Implement AcoustID API integration\n",
    "shared/beatport_api.py": "# Implemented — paste your session version here\n",
    "shared/discogs_api.py": "# TODO: Implement Discogs API integration\n",
    "shared/musicbrainz_api.py": "# TODO: Implement MusicBrainz API integration\n",
    "shared/spotify_api.py": "# TODO: Implement Spotify API integration\n",
    "tag/acoustid.py": "# TODO: Implement AcoustID tag integration\n",
    "tag/beatport.py": """from shared import beatport_api
from shared.metadata_utils import normalize_artist

def extract_ucp_metadata(track_json):
    title = track_json.get(\"name\")
    artist = ", ".join([a[\"name\"] for a in track_json.get(\"artists\", [])])
    album = track_json.get(\"release\", {}).get(\"name\")
    albumartist = ", ".join([a[\"name\"] for a in track_json.get(\"release\", {}).get(\"artists\", [])])
    date = track_json.get(\"release\", {}).get(\"release_date\", \"")[:10]
    tracknumber = track_json.get(\"track_number\", 0)
    discnumber = 1  # Beatport doesn’t provide disc info
    duration = track_json.get(\"duration_ms\", 0) / 1000.0
    isrc = track_json.get(\"isrc\")
    genre = track_json.get(\"genre\", {}).get(\"name\")
    explicit = False  # Beatport does not provide this field
    beatport_id = str(track_json.get(\"id\"))
    album_upc = track_json.get(\"release\", {}).get(\"upc\")
    cover = track_json.get(\"images\", {}).get(\"large\", {}).get(\"url\")

    return {
        \"title\": title,
        \"artist\": normalize_artist(artist),
        \"album\": album,
        \"albumartist\": normalize_artist(albumartist),
        \"date\": date,
        \"tracknumber\": tracknumber,
        \"discnumber\": discnumber,
        \"duration\": duration,
        \"isrc\": isrc,
        \"explicit\": explicit,
        \"genre\": genre,
        \"beatport_id\": beatport_id,
        \"album_upc\": album_upc,
        \"lyrics\": {
            \"synced\": \"\",
            \"unsynced\": \"\"
        },
        \"sources\": {
            \"primary\": \"beatport\",
            \"fallbacks\": []
        },
        \"cover_art_url\": cover
    }

def tag_from_beatport_id(track_id: str) -> dict:
    track = beatport_api.get_track(track_id)
    return extract_ucp_metadata(track)

def search_and_tag(query: str) -> dict:
    results = beatport_api.search_track(query)
    tracks = results.get(\"tracks\", {}).get(\"items\", [])
    if not tracks:
        raise ValueError(\"No results found for query: \" + query)
    return extract_ucp_metadata(tracks[0])
""",
    "tag/discogs.py": "# TODO: Implement Discogs tag integration\n",
    "tag/musicbrainz.py": "# TODO: Implement MusicBrainz tag integration\n",
    "tag/spotify.py": "# TODO: Implement Spotify tag integration\n",
}

def create_stub_files(base_dir: Path):
    for relative_path, content in MISSING_MODULES.items():
        target_path = base_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not target_path.exists():
            target_path.write_text(content)
            print(f"✅ Created: {relative_path}")
        else:
            print(f"⏭️ Already exists: {relative_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    create_stub_files(project_root)
