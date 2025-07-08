import typer
from pathlib import Path
from mutagen.flac import FLAC
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Use absolute imports to avoid circular import issues
from flaccid.shared.qobuz_api import QobuzAPI
from flaccid.shared.metadata_utils import validate_flac_file, get_existing_metadata, build_search_query

console = Console()
app = typer.Typer(help="Tag FLAC files using Qobuz metadata.")

async def apply_qobuz_tags(flac_path: str, metadata: dict):
    """Apply Qobuz metadata to FLAC file."""
    try:
        audio = FLAC(flac_path)

        # Basic metadata
        if "title" in metadata:
            audio["TITLE"] = metadata["title"]

        if "performer" in metadata:
            audio["ARTIST"] = metadata["performer"]["name"]

        if "album" in metadata:
            album = metadata["album"]
            audio["ALBUM"] = album["title"]

            if "artist" in album:
                audio["ALBUMARTIST"] = album["artist"]["name"]

            if "release_date_original" in album:
                audio["DATE"] = album["release_date_original"]

            if "genre" in album:
                audio["GENRE"] = album["genre"]["name"]

            if "label" in album:
                audio["LABEL"] = album["label"]["name"]

        # Track specific
        if "track_number" in metadata:
            audio["TRACKNUMBER"] = str(metadata["track_number"])

        if "media_number" in metadata:
            audio["DISCNUMBER"] = str(metadata["media_number"])

        if "composer" in metadata:
            audio["COMPOSER"] = metadata["composer"]["name"]

        # Quality info
        if "maximum_bit_depth" in metadata:
            audio["FLACCID_QOBUZ_BITDEPTH"] = str(metadata["maximum_bit_depth"])

        if "maximum_sampling_rate" in metadata:
            audio["FLACCID_QOBUZ_SAMPLERATE"] = str(metadata["maximum_sampling_rate"])

        # Save tags
        audio.save()
        return True

    except Exception as e:
        console.print(f"❌ Error tagging file: {e}", style="red")
        return False

@app.command("track")
def tag_track(flac_path: str, qobuz_id: str):
    """
    Tag a FLAC file with metadata from Qobuz by track ID.

    Args:
        flac_path: Path to the FLAC file to tag
        qobuz_id: Qobuz track ID
    """
    if not validate_flac_file(flac_path):
        console.print(f"❌ Invalid FLAC file: {flac_path}", style="red")
        raise typer.Exit(1)

    async def tag_process():
        async with QobuzAPI() as qobuz:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Fetching metadata from Qobuz...", total=None)

                metadata = await qobuz.get_track_metadata(qobuz_id)

                if metadata:
                    progress.update(task, description="Applying tags to FLAC file...")
                    success = await apply_qobuz_tags(flac_path, metadata)

                    if success:
                        console.print(f"✅ Successfully tagged: {Path(flac_path).name}", style="green")
                        console.print(f"   Title: {metadata.get('title', 'Unknown')}")
                        console.print(f"   Artist: {metadata.get('performer', {}).get('name', 'Unknown')}")
                        console.print(f"   Album: {metadata.get('album', {}).get('title', 'Unknown')}")
                    else:
                        console.print(f"❌ Failed to apply tags", style="red")
                        raise typer.Exit(1)
                else:
                    console.print(f"❌ Could not fetch metadata for ID: {qobuz_id}", style="red")
                    raise typer.Exit(1)

    asyncio.run(tag_process())

@app.command("search")
def search_and_tag(flac_path: str, query: str = None):
    """
    Search Qobuz and interactively tag a FLAC file.

    Args:
        flac_path: Path to the FLAC file to tag
        query: Search query (if not provided, will use existing file metadata)
    """
    if not validate_flac_file(flac_path):
        console.print(f"❌ Invalid FLAC file: {flac_path}", style="red")
        raise typer.Exit(1)

    # If no query provided, try to construct one from existing metadata
    if not query:
        metadata = get_existing_metadata(flac_path)
        query = build_search_query(metadata)
        if not query:
            query = typer.prompt("Enter search query")

    async def search_process():
        async with QobuzAPI() as qobuz:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Searching Qobuz...", total=None)

                results = await qobuz.search(query)

                if results and "tracks" in results and results["tracks"]["items"]:
                    tracks = results["tracks"]["items"]

                    console.print(f"\n🔍 Found {len(tracks)} results for: {query}")

                    for i, track in enumerate(tracks[:5]):  # Show top 5
                        album = track.get("album", {})
                        performer = track.get("performer", {})

                        console.print(f"\n{i+1}. {track.get('title', 'Unknown')}")
                        console.print(f"   Artist: {performer.get('name', 'Unknown')}")
                        console.print(f"   Album: {album.get('title', 'Unknown')}")
                        console.print(f"   Year: {album.get('release_date_original', 'Unknown')}")
                        console.print(f"   ID: {track.get('id', 'Unknown')}")

                    while True:
                        try:
                            choice = typer.prompt("\nSelect track (1-5) or 'q' to quit")
                            if choice.lower() == 'q':
                                return

                            idx = int(choice) - 1
                            if 0 <= idx < len(tracks):
                                selected_track = tracks[idx]
                                track_id = str(selected_track["id"])

                                console.print(f"\n📝 Tagging with: {selected_track.get('title', 'Unknown')}")
                                success = await apply_qobuz_tags(flac_path, selected_track)

                                if success:
                                    console.print(f"✅ Successfully tagged: {Path(flac_path).name}", style="green")
                                else:
                                    console.print(f"❌ Failed to apply tags", style="red")
                                return
                            else:
                                console.print("Invalid selection. Please try again.")
                        except ValueError:
                            console.print("Please enter a valid number or 'q' to quit.")
                else:
                    console.print(f"❌ No results found for: {query}", style="red")

    asyncio.run(search_process())

@app.command("batch")
def batch_tag(directory: str, recursive: bool = typer.Option(False, "--recursive", "-r", help="Process subdirectories recursively")):
    """
    Batch tag FLAC files in a directory by searching for each file.

    Args:
        directory: Directory containing FLAC files
        recursive: Process subdirectories recursively
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    # Find FLAC files
    if recursive:
        flac_files = list(dir_path.rglob("*.flac"))
    else:
        flac_files = list(dir_path.glob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {directory}", style="red")
        raise typer.Exit(1)

    console.print(f"🎵 Found {len(flac_files)} FLAC files")

    if not typer.confirm("Proceed with batch tagging?"):
        return

    for flac_file in flac_files:
        console.print(f"\n📁 Processing: {flac_file.name}")

        try:
            # Try to get existing metadata for search
            audio = FLAC(str(flac_file))
            title = audio.get("TITLE", [""])[0]
            artist = audio.get("ARTIST", [""])[0]

            if title and artist:
                query = f"{artist} {title}"
                console.print(f"🔍 Searching for: {query}")

                # Call search and tag with auto-select first result
                # This is a simplified version - in practice you might want more sophisticated matching
                typer.echo(f"Skipping {flac_file.name} - interactive mode required")
            else:
                console.print(f"⚠️  No existing metadata found for: {flac_file.name}")

        except Exception as e:
            console.print(f"❌ Error processing {flac_file.name}: {e}", style="red")
            continue
