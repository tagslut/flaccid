import requests

API_BASE = "https://api.discogs.com"
TOKEN = "SmVAvvDFVDWWILmFeBZNheDQltanDVWgSjmkWekw"
HEADERS = {"Authorization": f"Discogs token={TOKEN}", "User-Agent": "flaccid/1.0 (georges@user.email)"}

def search_release(query: str, limit=1):
    params = {"q": query, "type": "release", "per_page": limit}
    resp = requests.get(f"{API_BASE}/database/search", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def get_release(release_id: str):
    resp = requests.get(f"{API_BASE}/releases/{release_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_master(master_id: str):
    resp = requests.get(f"{API_BASE}/masters/{master_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()
