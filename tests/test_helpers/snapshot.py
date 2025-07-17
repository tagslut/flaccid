from __future__ import annotations

import json
import os
from pathlib import Path

SNAPSHOT_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "snapshots"


def assert_snapshot(data: dict, name: str) -> None:
    """Compare ``data`` against stored snapshot ``name``.

    Set the ``REGEN_SNAPSHOTS`` environment variable to regenerate the
    snapshot files.
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file = SNAPSHOT_DIR / f"{name}.json"
    if os.getenv("REGEN_SNAPSHOTS"):
        file.write_text(json.dumps(data, indent=2, sort_keys=True))
        return
    if not file.exists():
        raise FileNotFoundError(f"Snapshot {name} does not exist")
    expected = json.loads(file.read_text())
    assert data == expected
