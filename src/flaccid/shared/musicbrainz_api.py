import requests

API_BASE = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": "flaccid/1.0 (georges@user.email)"}

def search_recording(query: str, limit=1):
    params = {"query": query, "limit": limit, "fmt": "json"}
    resp = requests.get(f"{API_BASE}/recording/", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def get_recording(recording_id: str):
    params = {"fmt": "json"}
    resp = requests.get(f"{API_BASE}/recording/{recording_id}", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def get_release(release_id: str):
    params = {"fmt": "json"}
    resp = requests.get(f"{API_BASE}/release/{release_id}", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()
