from __future__ import annotations

"""Base plugin classes and metadata models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Self


@dataclass
class TrackMetadata:
    """Basic track metadata model."""

    title: str
    artist: str
    album: str
    track_number: int
    disc_number: int
    year: Optional[int] = None
    isrc: Optional[str] = None
    art_url: Optional[str] = None
    lyrics: Optional[str] = None


@dataclass
class AlbumMetadata:
    """Basic album metadata model."""

    title: str
    artist: str
    year: Optional[int] = None
    cover_url: Optional[str] = None


class MusicServicePlugin(ABC):
    """Abstract base for any music service plugin."""

    session: Any | None = None

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    @abstractmethod
    async def open(self) -> None:
        """Open network resources if needed."""

    @abstractmethod
    async def close(self) -> None:
        """Release network resources."""


class MetadataProviderPlugin(MusicServicePlugin, ABC):
    """Abstract plugin that can fetch track/album metadata."""

    @abstractmethod
    async def authenticate(self) -> None:
        """Perform service authentication."""

    @abstractmethod
    async def search_track(self, query: str) -> Any:
        """Search tracks by query."""

    @abstractmethod
    async def get_track(self, track_id: str) -> TrackMetadata:
        """Get full metadata for a track."""

    @abstractmethod
    async def get_album(self, album_id: str) -> AlbumMetadata:
        """Get full metadata for an album."""


class LyricsProviderPlugin(MusicServicePlugin, ABC):
    """Abstract plugin for lyrics providers."""

    @abstractmethod
    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Retrieve lyrics for *artist* and *title*."""
