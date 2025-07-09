

import os
import json
import time
import requests
from pathlib import Path

# Path to store tokens
TOKEN_PATH = Path.home() / ".config" / "flaccid" / "beatport_auth.json"
CLIENT_ID = "0GIvkCltVIuPkkwSJHp6NDb3s0potTjLBQr388Dd"
TOKEN_URL = "https://api.beatport.com/v4/auth/o/token/"

def load_token():
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "r") as f:
            return json.load(f)
    return {}

def save_token(data):
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_access_token():
    token_data = load_token()
    if not token_data:
        raise RuntimeError("No Beatport token found. Please authenticate first.")

    expires_at = token_data.get("expires_at", 0)
    if time.time() >= expires_at:
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("Missing refresh token.")

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": CLIENT_ID,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if not response.ok:
            raise RuntimeError("Failed to refresh Beatport token: " + response.text)
        new_token = response.json()
        new_token["expires_at"] = time.time() + new_token.get("expires_in", 3600)
        new_token["refresh_token"] = new_token.get("refresh_token", refresh_token)
        save_token(new_token)
        token_data = new_token

    return token_data["access_token"]

def _headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Accept": "application/json",
    }

def search_track(query):
    resp = requests.get("https://api.beatport.com/v4/catalog/search", params={"q": query}, headers=_headers())
    if not resp.ok:
        raise RuntimeError(f"Beatport search failed: {resp.status_code} - {resp.text}")
    return resp.json()

def get_track(track_id):
    url = f"https://api.beatport.com/v4/catalog/track/{track_id}"
    resp = requests.get(url, headers=_headers())
    if not resp.ok:
        raise RuntimeError(f"Failed to fetch track: {resp.status_code} - {resp.text}")
    return resp.json()

def get_release(release_id):
    url = f"https://api.beatport.com/v4/catalog/release/{release_id}"
    resp = requests.get(url, headers=_headers())
    if not resp.ok:
        raise RuntimeError(f"Failed to fetch release: {resp.status_code} - {resp.text}")
    return resp.json()