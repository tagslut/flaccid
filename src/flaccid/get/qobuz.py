"""Qobuz download helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path

from flaccid.plugins import QobuzPlugin


def download_track(track_id: str, dest: Path) -> bool:
    """Download a Qobuz track to ``dest``.

    Parameters
    ----------
    track_id:
        Identifier of the track on Qobuz.
    dest:
        Destination file path.

    Returns
    -------
    bool
        ``True`` if the download succeeded, ``False`` otherwise.
    """

    async def _run() -> bool:
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            return await plugin.download(track_id, dest)

    return asyncio.run(_run())
