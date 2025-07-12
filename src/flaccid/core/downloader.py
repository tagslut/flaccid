from pathlib import Path

import aiohttp


async def download_file(
    session: aiohttp.ClientSession, url: str, dest_path: Path
) -> bool:
    """Download *url* to *dest_path* using *session*."""
    async with session.get(url) as resp:
        if resp.status != 200:
            return False
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with dest_path.open("wb") as fh:
            async for chunk in resp.content.iter_chunked(1024):
                fh.write(chunk)
    return True
