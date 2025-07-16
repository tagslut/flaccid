"""Plugin registry."""
# Plugins package
from .apple import AppleMusicPlugin
from .beatport import BeatportPlugin
from .discogs import DiscogsPlugin
from .lyrics import LyricsPlugin
from .qobuz import QobuzPlugin
from .tidal import TidalPlugin

PLUGINS = {
    "apple": AppleMusicPlugin,
    "beatport": BeatportPlugin,
    "discogs": DiscogsPlugin,
    "lyrics": LyricsPlugin,
    "qobuz": QobuzPlugin,
    "tidal": TidalPlugin,
}

__all__ = [
    "PLUGINS",
    "AppleMusicPlugin",
    "BeatportPlugin",
    "DiscogsPlugin",
    "LyricsPlugin",
    "QobuzPlugin",
    "TidalPlugin",
]
