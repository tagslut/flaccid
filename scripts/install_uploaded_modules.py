#!/usr/bin/env python3
"""
Install uploaded FLACCID modules into the correct project folders.

Usage  (from the repo root):
    python scripts/install_uploaded_modules.py  /path/to/uploaded/files

If you omit the path argument it defaults to ./uploads
(where you can simply dump the .py files you downloaded).
"""

import sys
import shutil
from pathlib import Path

# ----------------------------------------------------------------------
# 1)  Map each uploaded file to its destination sub-folder
# ----------------------------------------------------------------------
DEST_MAP: dict[str, str] = {
    # shared APIs
    "beatport_api.py":   "shared",
    "discogs_api.py":    "shared",
    "musicbrainz_api.py":"shared",
    "spotify_api.py":    "shared",
    "acoustid_api.py":   "shared",
    # tag adapters
    "beatport.py":       "tag",
    "discogs.py":        "tag",
    "musicbrainz.py":    "tag",
    "spotify.py":        "tag",
    "acoustid.py":       "tag",
}

# ----------------------------------------------------------------------
def copy_file(src: Path, dest: Path) -> None:
    # If the file is already in the right place, skip.
    if src.resolve() == dest.resolve():
        print(f"⏭️  {src.name} already in correct folder – skipping.")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        yn = input(f"{dest} exists – overwrite? [y/N] ").strip().lower()
        if yn != "y":
            print("  skipped.")
            return

    shutil.copy2(src, dest)
    print(f"✅  {src.name}  →  {dest}")

# ----------------------------------------------------------------------
def copy_modules(src_dir: Path, project_root: Path) -> None:
    if not src_dir.exists():
        sys.exit(f"Source directory {src_dir} not found.")

    for fname, dest_sub in DEST_MAP.items():
        src_path = src_dir / fname
        dest_dir = project_root / dest_sub
        dest_path = dest_dir / fname

        # Skip files that aren't present in the uploads folder
        if not src_path.exists():
            print(f"⚠️  {fname} not found in {src_dir} — skipping.")
            continue

        copy_file(src_path, dest_path)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    # project root = two levels above this script (repo/scripts/…)
    project_root = Path(__file__).resolve().parent.parent
    # uploads folder given on CLI or default to ./uploads
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else project_root / "uploads"
    copy_modules(src_dir, project_root)
