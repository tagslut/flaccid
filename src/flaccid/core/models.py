# SPDX-License-Identifier: GPL-2.0-or-later
"""Canonical data models used throughout Flaccid."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, PositiveInt


class AudioFile(BaseModel):
    file_path: Path


class Tag(BaseModel):
    name: str
    value: str


class Metadata(BaseModel):
    title: str
    artist: str
    album: str
    year: Optional[str] = None
    track_number: Optional[str] = None
    total_tracks: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None


class Artist(BaseModel):
    name: str = Field(..., min_length=1)
    provider_id: Optional[str] = Field(
        None, description="ID of the artist in an external catalogue"
    )


class Track(BaseModel):
    track_number: PositiveInt
    title: str = Field(..., min_length=1)
    artists: List[Artist]
    duration_ms: Optional[int] = Field(
        None, ge=0, description="Duration in milliseconds"
    )


class Album(BaseModel):
    title: str = Field(..., min_length=1)
    artists: List[Artist]
    release_year: Optional[int] = Field(None, ge=1900, le=2100)
    tracks: List[Track]
    provider: str = Field(..., description="source name, e.g. 'tidal'")
