# Plugin Development Guide

FLACCID is built around a simple plugin architecture so that additional metadata
or download providers can be added without modifying the core codebase.
This document outlines the available interfaces, how plugins are discovered, and
provides some tips for writing tests.

## Plugin Interfaces

Plugins live in `flaccid.plugins` and subclass the abstract base classes defined
in `plugins/base.py`.

### MetadataProviderPlugin

`MetadataProviderPlugin` is used for services that provide metadata or download
capabilities. It inherits from `MusicServicePlugin` which implements asynchronous
context management. The required methods are:

- `open()` and `close()` – create and dispose of any network resources.
- `authenticate()` – perform API authentication.
- `search_track(query: str)` – return search results in any format.
- `get_track(track_id: str) -> TrackMetadata` – fetch full track metadata.
- `get_album(album_id: str) -> AlbumMetadata` – fetch full album metadata.

The helper method `fetch_cover_art(url: str)` downloads cover art using the
plugin's `aiohttp` session.

### LyricsProviderPlugin

`LyricsProviderPlugin` is a lighter interface for fetching lyrics. It requires a
single method `get_lyrics(artist: str, title: str) -> Optional[str]` in addition
to the `open()` and `close()` lifecycle methods from `MusicServicePlugin`.

### Metadata Models

`TrackMetadata` and `AlbumMetadata` are small dataclasses representing the data a
provider should return. See `plugins/base.py` for the available fields.

## Discovering Plugins

`PluginLoader` loads all built‑in providers from `flaccid/plugins`. It also
checks additional directories listed in the `FLACCID_PLUGIN_PATH` environment
variable. The variable is colon separated on Unix-like systems. Any Python files
found in these directories that define subclasses of `MetadataProviderPlugin`
are imported and registered automatically.

Example:

```bash
export FLACCID_PLUGIN_PATH=~/my-flaccid-plugins:/opt/other-plugins
```

Each custom plugin should define a unique `NAME` attribute so it can be selected
on the command line:

```bash
fla download myservice 1234 output.flac
```

## Example Skeleton

```python
from __future__ import annotations

import aiohttp
from typing import Any

from flaccid.plugins.base import (
    AlbumMetadata,
    MetadataProviderPlugin,
    TrackMetadata,
)


class MyServicePlugin(MetadataProviderPlugin):
    NAME = "myservice"

    async def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def authenticate(self) -> None:
        ...  # obtain tokens or start a session

    async def search_track(self, query: str) -> Any:
        ...

    async def get_track(self, track_id: str) -> TrackMetadata:
        return TrackMetadata(
            title="Example",
            artist="Artist",
            album="Album",
            track_number=1,
            disc_number=1,
        )

    async def get_album(self, album_id: str) -> AlbumMetadata:
        return AlbumMetadata(title="Album", artist="Artist")
```

## Testing Tips

- Use `PluginLoader(tmp_path)` in your tests to ensure your plugin module can be
  discovered from a temporary directory.
- Patch network calls with `unittest.mock.AsyncMock` to avoid hitting real
  endpoints during unit tests.
- Run `poetry run pytest` and `poetry run pre-commit run --all-files` before
  submitting a pull request.

