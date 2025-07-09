import os
import json
import time
import requests
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/flaccid/beatport_auth.json"
API_BASE = "https://api.beatport.com/v4"
CLIENT_ID = "0GIvkCltVIuPkkwSJHp6NDb3s0potTjLBQr388Dd"


def load_tokens():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_tokens(tokens):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(tokens, f)

def get_access_token():
    tokens = load_tokens()
    now = int(time.time())
    if tokens.get("access_token") and tokens.get("expires_at", 0) > now + 60:
        return tokens["access_token"]
    # Refresh
    data = {
        "grant_type": "refresh_token",
        "client_id": tokens.get("client_id", CLIENT_ID),
        "refresh_token": tokens["refresh_token"],
    }
    resp = requests.post(f"{API_BASE}/identity/token", data=data)
    resp.raise_for_status()
    result = resp.json()
    tokens["access_token"] = result["access_token"]
    tokens["expires_at"] = now + result.get("expires_in", 3600)
    save_tokens(tokens)
    return tokens["access_token"]

def _auth_headers():
    return {"Authorization": f"Bearer {get_access_token()}"}

def search_track(query: str, limit=1):
    url = f"{API_BASE}/catalog/search/tracks"
    params = {"q": query, "size": limit}
    resp = requests.get(url, headers=_auth_headers(), params=params)
    resp.raise_for_status()
    return resp.json()

def get_track(track_id: str):
    url = f"{API_BASE}/catalog/tracks/{track_id}"
    resp = requests.get(url, headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()

def get_release(release_id: str):
    url = f"{API_BASE}/catalog/releases/{release_id}"
    resp = requests.get(url, headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()
