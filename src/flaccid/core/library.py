"""Library management utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from mutagen.flac import FLAC
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
    text,
)
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
    # Create the FTS table for full-text search if it doesn't exist
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE VIRTUAL TABLE IF NOT EXISTS tracks_fts "
            "USING fts5(title, artist, album, path UNINDEXED)"
        )
    return engine, tracks


def index_files(db_path: Path, files: Iterable[Path]) -> None:
    """Index FLAC *files* into SQLite database at *db_path*."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        for path in files:
            audio = FLAC(str(path))
            values = {
                "path": str(path),
                "title": "".join(audio.get("title", [])),
                "artist": "".join(audio.get("artist", [])),
                "album": "".join(audio.get("album", [])),
            }
            result = session.execute(tracks.insert().values(**values))
            track_id = result.inserted_primary_key[0]
            session.execute(
                text(
                    "INSERT INTO tracks_fts(rowid, title, artist, album, path) "
                    "VALUES (:rowid, :title, :artist, :album, :path)"
                ),
                {"rowid": track_id, **values},
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
                track_id = session.execute(
                    select(tracks.c.id).where(tracks.c.path == str(path))
                ).scalar_one()
            else:
                result = session.execute(
                    tracks.insert().values(path=str(path), **values)
                )
                track_id = result.inserted_primary_key[0]
            session.execute(
                text("DELETE FROM tracks_fts WHERE rowid = :rowid"),
                {"rowid": track_id},
            )
            session.execute(
                text(
                    "INSERT INTO tracks_fts(rowid, title, artist, album, path) "
                    "VALUES (:rowid, :title, :artist, :album, :path)"
                ),
                {"rowid": track_id, "path": str(path), **values},
            )

        for old in db_set - disk_set:
            track_id = session.execute(
                select(tracks.c.id).where(tracks.c.path == old)
            ).scalar_one()
            session.execute(tracks.delete().where(tracks.c.id == track_id))
            session.execute(
                text("DELETE FROM tracks_fts WHERE rowid = :rowid"),
                {"rowid": track_id},
            )

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
                    track_id = session.execute(
                        select(self._tracks.c.id).where(
                            self._tracks.c.path == str(path)
                        )
                    ).scalar_one()
                else:
                    result = session.execute(
                        self._tracks.insert().values(path=str(path), **values)
                    )
                    track_id = result.inserted_primary_key[0]
                session.execute(
                    text("DELETE FROM tracks_fts WHERE rowid = :rowid"),
                    {"rowid": track_id},
                )
                session.execute(
                    text(
                        "INSERT INTO tracks_fts(rowid, title, artist, album, path) "
                        "VALUES (:rowid, :title, :artist, :album, :path)"
                    ),
                    {"rowid": track_id, "path": str(path), **values},
                )

            for old in db_set - disk_set:
                old_id = session.execute(
                    select(self._tracks.c.id).where(self._tracks.c.path == old)
                ).scalar_one()
                session.execute(
                    self._tracks.delete().where(self._tracks.c.id == old_id)
                )
                session.execute(
                    text("DELETE FROM tracks_fts WHERE rowid = :rowid"),
                    {"rowid": old_id},
                )

            session.commit()


def index_file(db_path: Path, file: Path) -> None:
    """Index a single FLAC *file* in *db_path*."""

    index_changed_files(db_path, [file])


def remove_file(db_path: Path, file: Path) -> None:
    """Remove *file* from the index at *db_path* if present."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        track_id = session.execute(
            select(tracks.c.id).where(tracks.c.path == str(file))
        ).scalar_one_or_none()
        if track_id is not None:
            session.execute(
                text("DELETE FROM tracks_fts WHERE rowid = :rowid"), {"rowid": track_id}
            )
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


def search_library(
    db_path: Path,
    query: str,
    *,
    sort: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Search the library using an FTS query."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        stmt = select(tracks).join_from(
            tracks, text("tracks_fts"), tracks.c.id == text("tracks_fts.rowid")
        )
        if query:
            stmt = stmt.where(text("tracks_fts MATCH :q")).params(q=query)

        if sort in {"path", "title", "artist", "album"}:
            stmt = stmt.order_by(getattr(tracks.c, sort))

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        rows = session.execute(stmt).mappings().all()
        return [dict(row) for row in rows]


def report_missing_metadata(db_path: Path) -> List[Dict[str, Any]]:
    """Return tracks missing title, artist, or album metadata."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        stmt = select(tracks).where(
            (tracks.c.title == "") | (tracks.c.artist == "") | (tracks.c.album == "")
        )
        rows = session.execute(stmt).mappings().all()
        return [dict(row) for row in rows]


def _collect_directory(directory: Path) -> Dict[str, Dict[str, Any]]:
    """Return mapping of relative file paths to basic metadata."""

    data: Dict[str, Dict[str, Any]] = {}
    for file_path in scan_directory(directory):
        audio = FLAC(str(file_path))
        data[str(file_path.relative_to(directory))] = {
            "title": "".join(audio.get("title", [])),
            "artist": "".join(audio.get("artist", [])),
            "album": "".join(audio.get("album", [])),
            "mtime": file_path.stat().st_mtime,
        }
    return data


def _collect_database(db_path: Path) -> Dict[str, Dict[str, Any]]:
    """Return mapping of file paths to metadata stored in *db_path*."""

    engine, tracks = _init_db(db_path)
    with Session(engine) as session:
        rows = session.execute(select(tracks)).mappings().all()
    return {
        row["path"]: {
            "title": row.get("title", ""),
            "artist": row.get("artist", ""),
            "album": row.get("album", ""),
        }
        for row in rows
    }


def diff_libraries(path_a: Path, path_b: Path) -> List[str]:
    """Return human-readable diffs between two libraries."""

    if path_a.is_dir() and path_b.is_dir():
        data_a = _collect_directory(path_a)
        data_b = _collect_directory(path_b)
    elif path_a.is_file() and path_b.is_file():
        data_a = _collect_database(path_a)
        data_b = _collect_database(path_b)
    else:
        raise ValueError("Both paths must be directories or database files")

    diffs: List[str] = []
    all_paths = sorted(set(data_a) | set(data_b))

    for rel in all_paths:
        if rel not in data_a:
            diffs.append(f"+ {rel}")
            continue
        if rel not in data_b:
            diffs.append(f"- {rel}")
            continue

        entry_a = data_a[rel]
        entry_b = data_b[rel]
        changes: List[str] = []

        for key in ("title", "artist", "album"):
            if entry_a.get(key) != entry_b.get(key):
                changes.append(f"{key}: {entry_a.get(key)} -> {entry_b.get(key)}")

        if "mtime" in entry_a and "mtime" in entry_b:
            if entry_a["mtime"] != entry_b["mtime"]:
                changes.append("timestamp changed")

        if changes:
            diffs.append(f"* {rel} | {'; '.join(changes)}")

    return diffs
