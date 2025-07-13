from __future__ import annotations

"""Library management utilities."""

from pathlib import Path
from typing import Iterable, List

from mutagen.flac import FLAC
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


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
                    tracks.update()
                    .where(tracks.c.path == str(path))
                    .values(**values)
                )
            else:
                session.execute(tracks.insert().values(path=str(path), **values))

        for old in db_set - disk_set:
            session.execute(tracks.delete().where(tracks.c.path == old))

        session.commit()


def watch_library(directory: Path, db_path: Path) -> None:
    """Watch *directory* for changes and update *db_path* accordingly."""

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import time

    class Handler(FileSystemEventHandler):
        def on_created(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                index_changed_files(db_path, [Path(event.src_path)])

        def on_modified(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                index_changed_files(db_path, [Path(event.src_path)])

        def on_deleted(self, event) -> None:  # type: ignore[override]
            if not event.is_directory and event.src_path.endswith(".flac"):
                engine, tracks = _init_db(db_path)
                with Session(engine) as sess:
                    sess.execute(tracks.delete().where(tracks.c.path == event.src_path))
                    sess.commit()

    observer = Observer()
    handler = Handler()
    observer.schedule(handler, str(directory), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
