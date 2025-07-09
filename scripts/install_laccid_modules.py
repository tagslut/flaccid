#!/usr/bin/env python3
"""
Auto-install FLACCID metadata modules wherever they are.

 • Searches the entire repo tree (and your $HOME/Downloads by default)
 • Detects any of the ten approved module filenames
 • Copies each into shared/ or tag/ as appropriate
 • Prompts before overwriting existing files

Run from the repo root:
    python scripts/auto_install_flaccid_modules.py
"""

import os
import shutil
from pathlib import Path

# ------------------------------------------------------------------ #
DEST_MAP = {
    #   file-name            →   destination sub-folder
    "beatport_api.py":   "shared",
    "discogs_api.py":    "shared",
    "musicbrainz_api.py":"shared",
    "spotify_api.py":    "shared",
    "acoustid_api.py":   "shared",
    "beatport.py":       "tag",
    "discogs.py":        "tag",
    "musicbrainz.py":    "tag",
    "spotify.py":        "tag",
    "acoustid.py":       "tag",
}
# Paths we’ll scan for loose files
EXTRA_SEARCH_DIRS = [
    Path.home() / "Downloads",  # common download location
]
# ------------------------------------------------------------------ #

def locate_candidates(repo_root: Path) -> dict[str, Path]:
    """Return {filename: actual_path} for each file we find."""
    found: dict[str, Path] = {}

    # Walk repo
    for dirpath, _, files in os.walk(repo_root):
        for fname in files:
            if fname in DEST_MAP:
                found.setdefault(fname, Path(dirpath) / fname)

    # Walk extra dirs
    for extra in EXTRA_SEARCH_DIRS:
        if extra.exists():
            for fname in DEST_MAP:
                cand = extra / fname
                if cand.exists():
                    found.setdefault(fname, cand)

    return found

def copy_file(src: Path, dest: Path) -> None:
    """
    Copy a module file into its destination folder, but skip if the file
    is already located there. Prompt before overwriting any existing file.
    """
    # Skip if source and destination are identical
    try:
        if src.resolve() == dest.resolve():
            print(f"⏭️  {src.name} already in correct folder – skipping.")
            return
    except FileNotFoundError:
        # Source was removed mid‑run; safely skip
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        yn = input(f"{dest} exists – overwrite? [y/N] ").strip().lower()
        if yn != "y":
            print("  skipped.")
            return

    shutil.copy2(src, dest)
    print(f"✅  {src.name}  →  {dest}")

def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    found = locate_candidates(repo_root)

    print("=== FLACCID module auto-installer ===")
    if not found:
        print("No candidate files located. Make sure the .py files "
              "are somewhere under the repo or in ~/Downloads.")
        return

    for fname, subfolder in DEST_MAP.items():
        src_path = found.get(fname)
        dest_path = repo_root / subfolder / fname
        if src_path:
            copy_file(src_path, dest_path)
        else:
            print(f"⚠️  {fname} not found – not installed.")

if __name__ == "__main__":
    main()
