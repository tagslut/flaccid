from __future__ import annotations

"""Library management utilities."""

from pathlib import Path
from typing import Iterable, List

from mutagen.flac import FLAC
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
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
