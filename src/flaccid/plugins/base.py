from __future__ import annotations

#!/usr/bin/env python3
"""
Base plugin classes for the FLACCID CLI.

This module defines the interfaces that plugins must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@dataclass
class TrackMetadata:
    """Metadata for a music track."""

    title: str
    artist: str
    album: str
    track_number: int
    disc_number: int = 1
    year: Optional[int] = None
    isrc: Optional[str] = None
    lyrics: Optional[str] = None
    art_url: Optional[str] = None


@dataclass
class AlbumMetadata:
    """Metadata for a music album."""

    title: str
    artist: str
    year: Optional[int] = None
    cover_url: Optional[str] = None


@runtime_checkable
class MetadataProviderPlugin(Protocol):
    """Interface for metadata provider plugins."""

    async def open(self) -> None:
        """Initialize the plugin."""
        ...

    async def close(self) -> None:
        """Clean up plugin resources."""
        ...

    async def get_track(self, track_id: str) -> TrackMetadata:
        """Get metadata for a track."""
        ...

    async def fetch_cover_art(self, url: str) -> Optional[bytes]:
        """Fetch cover art for a track."""
        ...


@runtime_checkable
class LyricsProviderPlugin(Protocol):
    """Interface for lyrics provider plugins."""

    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Get lyrics for a track."""
        ...


@runtime_checkable
class DownloadProviderPlugin(Protocol):
    """Interface for download provider plugins."""

    async def download_track(self, track_id: str, dest: Path) -> bool:
        """Download a track to the destination path."""
        ...


class BasePlugin(ABC):
    """Base class for plugins that implements __enter__ and __exit__."""

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @abstractmethod
    async def open(self) -> None:
        """Initialize the plugin."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up plugin resources."""
        pass
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

    async def fetch_cover_art(self, url: str) -> bytes:
        """Return raw bytes for the cover art at ``url``."""
        if not self.session:
            await self.open()
        assert self.session is not None
        async with self.session.get(url) as resp:
            return await resp.read()


class LyricsProviderPlugin(MusicServicePlugin, ABC):
    """Abstract plugin for lyrics providers."""

    @abstractmethod
    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Retrieve lyrics for *artist* and *title*."""
