from __future__ import annotations

"""Library management utilities."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from mutagen.flac import FLAC
from sqlalchemy import (Column, Integer, MetaData, String, Table,
                        create_engine, select)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Internal state for active observers. Keys are watched directories and values
# are watchdog Observer instances. This allows starting and stopping watching
# programmatically through the API.
# Use Any for Observer to avoid mypy issues if watchdog is missing at type-check time
# ---------------------------------------------------------------------------
_WATCHERS: Dict[Path, Any] = {}


def scan_directory(directory: Path) -> List[Path]:
    """Recursively scan *directory* for FLAC files."""

    return [p for p in directory.rglob("*.flac") if p.is_file()]


def _init_db(db_path: Path) -> tuple[Engine, Table]:
    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()
    tracks = Table(
        "tracks",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("path", String, unique=True, nullable=False),
        Column("title", String),
        Column("artist", String),
        Column("album", String),
    )
    metadata.create_all(engine)
    return engine, tracks


def index_files(db_path: Path, files: Iterable[Path]) -> None:
    """Index FLAC *files* into SQLite database at *db_path*."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        for path in files:
            audio = FLAC(str(path))
            session.execute(
                tracks.insert().values(
                    path=str(path),
                    title="".join(audio.get("title", [])),
                    artist="".join(audio.get("artist", [])),
                    album="".join(audio.get("album", [])),
                )
            )
        session.commit()


def index_changed_files(db_path: Path, files: Iterable[Path]) -> None:
    """Update the index at *db_path* to match *files*."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        disk_set = {str(p) for p in files}
        rows = session.execute(select(tracks.c.path)).scalars().all()
        db_set = set(rows)

        for path in files:
            audio = FLAC(str(path))
            values = {
                "title": "".join(audio.get("title", [])),
                "artist": "".join(audio.get("artist", [])),
                "album": "".join(audio.get("album", [])),
            }

            if str(path) in db_set:
                session.execute(
                    tracks.update().where(tracks.c.path == str(path)).values(**values)
                )
            else:
                session.execute(tracks.insert().values(path=str(path), **values))

        for old in db_set - disk_set:
            session.execute(tracks.delete().where(tracks.c.path == old))

        session.commit()


class IncrementalIndexer:
    """Incrementally index FLAC files by modification time."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._mtimes: Dict[Path, float] = {}
        self._engine, self._tracks = _init_db(db_path)

    def index(self, files: Iterable[Path]) -> None:
        """Index *files*, updating only those that changed."""

        disk_set = {str(p) for p in files}
        changed: List[Path] = []

        for path in files:
            mtime = path.stat().st_mtime
            if self._mtimes.get(path) != mtime:
                changed.append(path)
            self._mtimes[path] = mtime

        with Session(self._engine) as session:
            rows = session.execute(select(self._tracks.c.path)).scalars().all()
            db_set = set(rows)

            for path in changed:
                audio = FLAC(str(path))
                values = {
                    "title": "".join(audio.get("title", [])),
                    "artist": "".join(audio.get("artist", [])),
                    "album": "".join(audio.get("album", [])),
                }

                if str(path) in db_set:
                    session.execute(
                        self._tracks.update()
                        .where(self._tracks.c.path == str(path))
                        .values(**values)
                    )
                else:
                    session.execute(
                        self._tracks.insert().values(path=str(path), **values)
                    )

            for old in db_set - disk_set:
                session.execute(self._tracks.delete().where(self._tracks.c.path == old))

            session.commit()


def index_file(db_path: Path, file: Path) -> None:
    """Index a single FLAC *file* in *db_path*."""

    index_changed_files(db_path, [file])


def remove_file(db_path: Path, file: Path) -> None:
    """Remove *file* from the index at *db_path* if present."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        session.execute(tracks.delete().where(tracks.c.path == str(file)))
        session.commit()


def start_watching(directories: Sequence[Path], db_path: Path) -> None:
    """Start watching *directories* and update *db_path* on changes."""
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class Handler(FileSystemEventHandler):
        def on_created(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                index_file(db_path, Path(event.src_path))

        def on_modified(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                index_file(db_path, Path(event.src_path))

        def on_deleted(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                remove_file(db_path, Path(event.src_path))

    for directory in directories:
        if directory in _WATCHERS:
            continue
        observer: Any = Observer()
        handler = Handler()
        observer.schedule(handler, str(directory), recursive=True)
        observer.start()
        _WATCHERS[directory] = observer


def stop_watching(directories: Sequence[Path]) -> None:
    """Stop watching each directory in *directories* if active."""
    for directory in directories:
        observer = _WATCHERS.pop(directory, None)
        if observer is not None:
            observer.stop()
            observer.join()


def watch_library(directories: Sequence[Path], db_path: Path) -> None:
    """Block and watch *directories*, updating *db_path* until interrupted."""

    import time

    start_watching(directories, db_path)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_watching(directories)
