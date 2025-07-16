#!/usr/bin/env python3
"""
Tag commands for the FLACCID CLI.

This module provides the 'meta' commands for tagging audio files.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command("apple")
def apple_command(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""
    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)


#!/usr/bin/env python3
"""
Tag commands for the FLACCID CLI.

This module provides the 'meta' commands for tagging audio files.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command()
def apple(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""
    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)


import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command()
def apple(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""
    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)


"""
Tag commands for the FLACCID CLI.
#!/usr/bin/env python3
"""
Tag commands for the FLACCID CLI.

This module provides the 'meta' commands for tagging audio files.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command("apple")
def apple_command(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""
    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)
This module provides the 'meta' commands for tagging audio files.
"""
#!/usr/bin/env python3
"""
Tag commands for the FLACCID CLI.

This module provides the 'meta' commands for tagging audio files.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command("apple")
def apple_command(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""
    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)


import typer

app = typer.Typer()


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
):
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option("apple", help="The metadata provider to use"),
):
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    metadata_file: str = typer.Option(..., help="Path to the metadata file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from {metadata_file} to {file_path}")
    if not yes:
        typer.echo("Use --yes to skip confirmation")
    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)
