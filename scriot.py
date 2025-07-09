#!/usr/bin/env python3
from pathlib import Path, shutil

repo = Path(__file__).resolve().parent.parent
src_pkg = repo / "src" / "flaccid"

for sub in ("shared", "tag"):
    dup = repo / sub
    if dup.exists():
        for f in dup.glob("*.py"):
            dest = src_pkg / sub / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            print("→", f.relative_to(repo), "→", dest.relative_to(repo))
            dest.write_bytes(f.read_bytes())  # overwrite
        shutil.rmtree(dup)

print("Now: fix merge markers, update pyproject, then `pip install -e .`")
