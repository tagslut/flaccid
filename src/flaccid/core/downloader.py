from __future__ import annotations

from pathlib import Path

#!/usr/bin/env python3
"""
File download utilities for the FLACCID CLI.
"""

import asyncio
import os
from typing import Optional

import aiohttp
from rich.progress import Progress, TaskID


async def download_file(
    session: aiohttp.ClientSession,
    url: str,
    dest_path: Path,
    progress: Optional[Progress] = None,
    task_id: Optional[TaskID] = None,
) -> bool:
    """Download a file from a URL to a local path.

    Args:
        session: HTTP session to use
        url: URL to download from
        dest_path: Path to save the file to
        progress: Optional progress reporter
        task_id: Task ID for progress reporting

    Returns:
        True if the download was successful
    """
    temp_path = dest_path.with_suffix(".tmp")
    os.makedirs(dest_path.parent, exist_ok=True)

    try:
        async with session.get(url) as response:
            if not response.ok:
                print(f"Failed to download {url}: {response.status}")
                return False

            total_size = int(response.headers.get("Content-Length", 0))
            if progress and task_id is not None:
                progress.update(task_id, total=total_size)

            with open(temp_path, "wb") as f:
                bytes_downloaded = 0
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if progress and task_id is not None:
                        progress.update(task_id, completed=bytes_downloaded)

        # Rename temporary file to destination
        temp_path.rename(dest_path)
        return True

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


async def download_files(
    session: aiohttp.ClientSession, urls: list[tuple[str, Path]]
) -> list[Path]:
    """Download multiple files concurrently.

    Args:
        session: HTTP session to use
        urls: List of (url, dest_path) pairs

    Returns:
        List of successfully downloaded file paths
    """
    with Progress() as progress:
        tasks = []
        for url, dest_path in urls:
            task_id = progress.add_task(f"Downloading {dest_path.name}", total=0)
            tasks.append(download_file(session, url, dest_path, progress, task_id))

        results = await asyncio.gather(*tasks)
        return [path for (success, (_, path)) in zip(results, urls) if success]


