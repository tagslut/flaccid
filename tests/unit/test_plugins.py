import os
from unittest.mock import patch

import pytest

from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.qobuz import QobuzPlugin


@pytest.mark.asyncio
async def test_qobuz_plugin_auth(monkeypatch):
    monkeypatch.setattr("keyring.get_password", lambda service, user: "secret")
    with patch.dict(os.environ, {"QOBUZ_APP_ID": "id"}, clear=False):
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            assert plugin.token == "secret"


def test_track_metadata_dataclass():
    meta = TrackMetadata(
        title="Song",
        artist="Artist",
        album="Album",
        track_number=1,
        disc_number=1,
        year=2020,
    )
    assert meta.title == "Song"
    assert meta.year == 2020
