"""Unit tests for the persistent library layer."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from flaccid.core import library


def test_scan_directory(tmp_path: Path):
    flac = tmp_path / "test.flac"
    flac.write_bytes(b"\x00\x00")
    other = tmp_path / "skip.mp3"
    other.write_text("nope")

    files = library.scan_directory(tmp_path)
    assert flac in files
    assert other not in files


def test_index_changed_files(tmp_path: Path, monkeypatch):
    db = tmp_path / "lib.db"
    f1 = tmp_path / "a.flac"
    f2 = tmp_path / "b.flac"
    f1.write_text("d1")
    f2.write_text("d2")

    class FakeFLAC(dict):
        def __init__(self, path: str) -> None:  # noqa: D401 - simple stub
            super().__init__()
            self["title"] = [Path(path).stem]
            self["artist"] = ["A"]
            self["album"] = ["B"]

    monkeypatch.setattr(library, "FLAC", FakeFLAC)

    library.index_files(db, [f1])

    def changed_flac(path: str) -> FakeFLAC:
        flac = FakeFLAC(path)
        if Path(path) == f1:
            flac["title"] = ["new"]
        return flac

    monkeypatch.setattr(library, "FLAC", changed_flac)
    library.index_changed_files(db, [f1, f2])

    engine, tracks = library._init_db(db)
    with Session(engine) as session:
        rows = {
            row.path: (row.title, row.artist, row.album)
            for row in session.execute(select(tracks)).all()
        }

    assert set(rows) == {str(f1), str(f2)}
    assert rows[str(f1)][0] == "new"

    library.index_changed_files(db, [f2])
    with Session(engine) as session:
        paths = {row.path for row in session.execute(select(tracks.c.path))}
    assert paths == {str(f2)}


def test_watch_library(monkeypatch, tmp_path: Path):
    db = tmp_path / "lib.db"
    captured: dict[str, object] = {}

    class FakeObserver:
        def schedule(self, handler, path, recursive=True) -> None:
            captured["handler"] = handler

        def start(self) -> None:
            pass

        def stop(self) -> None:
            captured["stopped"] = True

        def join(self) -> None:
            pass

    monkeypatch.setattr("watchdog.observers.Observer", FakeObserver)
    monkeypatch.setattr(
        "time.sleep", lambda t=1: (_ for _ in ()).throw(KeyboardInterrupt())
    )

    class FakeFLAC(dict):
        def __init__(self, path: str) -> None:
            super().__init__()
            self["title"] = ["t"]
            self["artist"] = ["a"]
            self["album"] = ["b"]

    monkeypatch.setattr(library, "FLAC", FakeFLAC)

    library.watch_library(tmp_path, db)

    handler = captured["handler"]
    new_file = tmp_path / "c.flac"
    new_file.write_text("data")
    event = type("E", (), {"src_path": str(new_file), "is_directory": False})()
    handler.on_created(event)  # type: ignore[attr-defined]

    engine, tracks = library._init_db(db)
    with Session(engine) as session:
        paths = {row.path for row in session.execute(select(tracks.c.path))}

    assert str(new_file) in paths
    assert captured.get("stopped") is True


def test_start_stop_watching(monkeypatch, tmp_path: Path) -> None:
    """Starting and stopping a watcher should manage observers properly."""

    db = tmp_path / "lib.db"
    events: dict[str, object] = {}

    class FakeObserver:
        def schedule(self, handler, path, recursive=True) -> None:
            events["handler"] = handler

        def start(self) -> None:
            events["started"] = True

        def stop(self) -> None:
            events["stopped"] = True

        def join(self) -> None:
            events["joined"] = True

    monkeypatch.setattr("watchdog.observers.Observer", FakeObserver)
    monkeypatch.setattr(
        library, "index_file", lambda dbp, p: events.setdefault("indexed", []).append(p)
    )
    monkeypatch.setattr(
        library,
        "remove_file",
        lambda dbp, p: events.setdefault("removed", []).append(p),
    )

    library.start_watching(tmp_path, db)
    assert events.get("started") is True

    handler = events["handler"]
    flac = tmp_path / "x.flac"
    flac.write_text("data")
    ev = type("E", (), {"src_path": str(flac), "is_directory": False})()
    handler.on_created(ev)  # type: ignore[attr-defined]
    assert flac in events.get("indexed", [])

    library.stop_watching(tmp_path)
    assert events.get("stopped") is True
    assert events.get("joined") is True
