#!/usr/bin/env python3
"""
Move finished modules from top-level shared/ and tag/ into
src/flaccid/shared and src/flaccid/tag, then delete the duplicates.
"""

import shutil
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
pkg_root  = repo_root / "src" / "flaccid"

def move_tree(subfolder: str) -> None:
    dup = repo_root / subfolder          # e.g. ./shared or ./tag
    if not dup.exists():
        return
    dest_base = pkg_root / subfolder
    dest_base.mkdir(parents=True, exist_ok=True)

    for file in dup.glob("*.py"):
        dest = dest_base / file.name
        print(f"→  {file.relative_to(repo_root)}  →  {dest.relative_to(repo_root)}")
        shutil.copy2(file, dest)   # overwrite if exists

    shutil.rmtree(dup)
    print(f"🗑️  removed duplicate folder {dup.relative_to(repo_root)}")

if __name__ == "__main__":
    for sub in ("shared", "tag"):
        move_tree(sub)
    print("\nDone.  Now fix any merge-conflict markers, ensure "
          "`pyproject.toml` has ONE [tool.poetry.packages] section, then run:\n"
          "    pip install -e .")