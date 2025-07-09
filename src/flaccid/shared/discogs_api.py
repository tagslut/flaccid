"""
AcoustID fingerprint lookup utilities for FLACCID.

Functions exported
------------------
generate_fingerprint(audio_path) -> (fingerprint: str, duration: int)
lookup_mbids(fingerprint, duration, max_results=3) -> list[dict]
"""

from __future__ import annotations

import subprocess
import json
import os
import requests
from pathlib import Path
from typing import Tuple, List

# ----------------------------------------------------------------------
API_KEY = "W0BiiyEnkH"  # Your AcoustID API key
API_URL = "https://api.acoustid.org/v2/lookup"
FP_BINARY = "fpcalc"    # must be in PATH; install via `brew install chromaprint`
# ----------------------------------------------------------------------

class AcoustIDError(RuntimeError):
    """Raised on AcoustID lookup failures."""


def generate_fingerprint(audio_path: str | Path) -> Tuple[str, int]:
    """
    Run fpcalc on *audio_path* and return (fingerprint, duration_seconds).

    Requires the fpcalc binary (Chromaprint) to be installed and accessible
    in the system PATH.
    """
    audio_path = Path(audio_path).expanduser().resolve()
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    try:
        result = subprocess.run(
            [FP_BINARY, "-json", str(audio_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise AcoustIDError(
            "fpcalc executable not found. Install Chromaprint "
            "(e.g., `brew install chromaprint` on macOS)."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise AcoustIDError(f"fpcalc failed: {exc.stderr}") from exc

    data = json.loads(result.stdout)
    return data["fingerprint"], int(data["duration"])


def lookup_mbids(
    fingerprint: str,
    duration: int,
    max_results: int = 3,
    meta: str = "recordings+recordingids+releaseids+compress"
) -> List[dict]:
    """
    Query AcoustID and return a list of result dicts.

      • fingerprint — Chromaprint string from `generate_fingerprint`
      • duration    — length of the audio in seconds
      • max_results — how many matches to return (default 3)
      • meta        — AcoustID meta flags (keep default)

    Each result dict contains keys like "score", "recordings", etc.
    Raise AcoustIDError on HTTP or API failures.
    """
    params = {
        "client": API_KEY,
        "fingerprint": fingerprint,
        "duration": duration,
        "meta": meta,
        "format": "json",
    }
    resp = requests.post(API_URL, data=params, timeout=10)
    if resp.status_code != 200:
        raise AcoustIDError(f"HTTP {resp.status_code}: {resp.text}")

    payload = resp.json()
    if payload.get("status") != "ok":
        raise AcoustIDError(f"API error: {payload}")

    return payload.get("results", [])[:max_results]


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # minimal manual test
    import sys, pprint

    if len(sys.argv) != 2:
        print("Usage: python -m shared.acoustid_api <audio_file>")
        sys.exit(1)

    fp, dur = generate_fingerprint(sys.argv[1])
    print("Fingerprint generated OK. Duration:", dur, "sec")
    results = lookup_mbids(fp, dur)
    pprint.pp(results)