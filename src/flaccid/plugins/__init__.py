"""Plugin registry."""

from __future__ import annotations

from .registry import PLUGINS, get_provider
from .apple import AppleMusicPlugin
from .beatport import BeatportPlugin
from .discogs import DiscogsPlugin
from .lyrics import LyricsPlugin, LyricsOvhProvider
from .genius import GeniusPlugin
from .musixmatch import MusixmatchPlugin
from .qobuz import QobuzPlugin
from .tidal import TidalPlugin

__all__ = [
    "PLUGINS",
    "get_provider",
    "AppleMusicPlugin",
    "BeatportPlugin",
    "DiscogsPlugin",
    "LyricsPlugin",
    "LyricsOvhProvider",
    "GeniusPlugin",
    "MusixmatchPlugin",
    "QobuzPlugin",
    "TidalPlugin",
]
