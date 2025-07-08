import typer
from pathlib import Path
from mutagen.flac import FLAC
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..shared.apple_api import AppleAPI
from ..shared.metadata_utils import validate_flac_file, get_existing_metadata, build_search_query, extract_isrc_from_flac

console = Console()
app = typer.Typer(help="Tag FLAC files using Apple Music metadata.")

def apple_to_flac_metadata(apple_metadata: dict) -> dict:
    """Convert Apple Music metadata to FLAC tags."""
    flac_tags = {}

    # Basic metadata
    if "trackName" in apple_metadata:
        flac_tags["TITLE"] = apple_metadata["trackName"]

    if "artistName" in apple_metadata:
        flac_tags["ARTIST"] = apple_metadata["artistName"]

    if "collectionName" in apple_metadata:
        flac_tags["ALBUM"] = apple_metadata["collectionName"]

    if "collectionArtistName" in apple_metadata:
        flac_tags["ALBUMARTIST"] = apple_metadata["collectionArtistName"]

    # Release date
    if "releaseDate" in apple_metadata:
        release_date = apple_metadata["releaseDate"]
        if "T" in release_date:
            year = release_date.split("T")[0].split("-")[0]
            flac_tags["DATE"] = year

    # Track and disc numbers
    if "trackNumber" in apple_metadata:
        flac_tags["TRACKNUMBER"] = str(apple_metadata["trackNumber"])

    if "trackCount" in apple_metadata:
        flac_tags["TOTALTRACKS"] = str(apple_metadata["trackCount"])

    if "discNumber" in apple_metadata:
        flac_tags["DISCNUMBER"] = str(apple_metadata["discNumber"])

    if "discCount" in apple_metadata:
        flac_tags["TOTALDISCS"] = str(apple_metadata["discCount"])

    # Genre
    if "primaryGenreName" in apple_metadata:
        flac_tags["GENRE"] = apple_metadata["primaryGenreName"]

    # ISRC
    if "isrc" in apple_metadata:
        flac_tags["ISRC"] = apple_metadata["isrc"]

    # Apple-specific metadata
    if "trackId" in apple_metadata:
        flac_tags["FLACCID_APPLE_TRACKID"] = str(apple_metadata["trackId"])

    if "collectionId" in apple_metadata:
        flac_tags["FLACCID_APPLE_ALBUMID"] = str(apple_metadata["collectionId"])

    if "artistId" in apple_metadata:
        flac_tags["FLACCID_APPLE_ARTISTID"] = str(apple_metadata["artistId"])

    # Copyright
    if "copyright" in apple_metadata:
        flac_tags["COPYRIGHT"] = apple_metadata["copyright"]

    # Country
    if "country" in apple_metadata:
        flac_tags["FLACCID_APPLE_COUNTRY"] = apple_metadata["country"]

    # Explicit content
    if "trackExplicitness" in apple_metadata:
        flac_tags["FLACCID_APPLE_EXPLICIT"] = apple_metadata["trackExplicitness"]

    return flac_tags

async def apply_apple_tags(flac_path: str, metadata: dict):
    """Apply Apple Music metadata to FLAC file."""
    try:
        audio = FLAC(flac_path)

        # Convert Apple metadata to FLAC tags
        flac_tags = apple_to_flac_metadata(metadata)

        # Apply all tags
        for key, value in flac_tags.items():
            if value:  # Only set non-empty values
                audio[key] = value

        audio.save()
        return True

    except Exception as e:
        console.print(f"❌ Error tagging file: {e}", style="red")
        return False

@app.command("isrc")
def tag_by_isrc(flac_path: str, isrc: str = None):
    """
    Tag a FLAC file with Apple Music metadata using ISRC.

    Args:
        flac_path: Path to the FLAC file to tag
        isrc: ISRC code (if not provided, will try to extract from file)
    """
    if not validate_flac_file(flac_path):
        console.print(f"❌ Invalid FLAC file: {flac_path}", style="red")
        raise typer.Exit(1)

    # Try to extract ISRC from file if not provided
    if not isrc:
        isrc = extract_isrc_from_flac(flac_path)
        if not isrc:
            console.print(f"❌ No ISRC provided and none found in file", style="red")
            raise typer.Exit(1)
        else:
            console.print(f"📀 Using ISRC from file: {isrc}")

    async def tag_process():
        async with AppleAPI() as apple:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Looking up ISRC on Apple Music...", total=None)

                metadata = await apple.lookup_by_isrc(isrc)

                if metadata:
                    progress.update(task, description="Applying tags to FLAC file...")
                    success = await apply_apple_tags(flac_path, metadata)

                    if success:
                        console.print(f"✅ Successfully tagged: {Path(flac_path).name}", style="green")
                        console.print(f"   Title: {metadata.get('trackName', 'Unknown')}")
                        console.print(f"   Artist: {metadata.get('artistName', 'Unknown')}")
                        console.print(f"   Album: {metadata.get('collectionName', 'Unknown')}")
                        console.print(f"   ISRC: {metadata.get('isrc', isrc)}")
                    else:
                        console.print(f"❌ Failed to apply tags", style="red")
                        raise typer.Exit(1)
                else:
                    console.print(f"❌ No results found for ISRC: {isrc}", style="red")
                    raise typer.Exit(1)

    asyncio.run(tag_process())

@app.command("search")
def search_and_tag(flac_path: str, query: str = None):
    """
    Search Apple Music and interactively tag a FLAC file.

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
        async with AppleAPI() as apple:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Searching Apple Music...", total=None)

                results = await apple.search(query)

                if results and "results" in results:
                    tracks = results["results"]
                    console.print(f"\n🔍 Found {len(tracks)} results for: {query}")

                    for i, track in enumerate(tracks[:5]):  # Show top 5
                        console.print(f"\n{i+1}. {track.get('trackName', 'Unknown')}")
                        console.print(f"   Artist: {track.get('artistName', 'Unknown')}")
                        console.print(f"   Album: {track.get('collectionName', 'Unknown')}")
                        console.print(f"   Year: {track.get('releaseDate', 'Unknown')[:4] if track.get('releaseDate') else 'Unknown'}")
                        console.print(f"   Genre: {track.get('primaryGenreName', 'Unknown')}")
                        if track.get('isrc'):
                            console.print(f"   ISRC: {track.get('isrc')}")

                    while True:
                        try:
                            choice = typer.prompt("\nSelect track (1-5) or 'q' to quit")
                            if choice.lower() == 'q':
                                return

                            idx = int(choice) - 1
                            if 0 <= idx < len(tracks):
                                selected_track = tracks[idx]

                                console.print(f"\n📝 Tagging with: {selected_track.get('trackName', 'Unknown')}")
                                success = await apply_apple_tags(flac_path, selected_track)

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
def batch_tag_by_isrc(directory: str, recursive: bool = typer.Option(False, "--recursive", "-r", help="Process subdirectories recursively")):
    """
    Batch tag FLAC files using embedded ISRC codes.

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

    # Count files with ISRC
    files_with_isrc = []
    for flac_file in flac_files:
        isrc = extract_isrc_from_flac(str(flac_file))
        if isrc:
            files_with_isrc.append((flac_file, isrc))

    console.print(f"📀 {len(files_with_isrc)} files have ISRC codes")

    if not files_with_isrc:
        console.print("❌ No files with ISRC codes found", style="red")
        raise typer.Exit(1)

    if not typer.confirm("Proceed with batch tagging?"):
        return

    async def batch_process():
        async with AppleAPI() as apple:
            for flac_file, isrc in files_with_isrc:
                console.print(f"\n📁 Processing: {flac_file.name}")
                console.print(f"   ISRC: {isrc}")

                try:
                    metadata = await apple.lookup_by_isrc(isrc)

                    if metadata:
                        success = await apply_apple_tags(str(flac_file), metadata)

                        if success:
                            console.print(f"   ✅ Tagged successfully", style="green")
                        else:
                            console.print(f"   ❌ Failed to apply tags", style="red")
                    else:
                        console.print(f"   ⚠️  No Apple Music match found", style="yellow")

                except Exception as e:
                    console.print(f"   ❌ Error: {e}", style="red")
                    continue

    asyncio.run(batch_process())

@app.command("track")
def tag_track(flac_path: str, track_id: str):
    """
    Tag a FLAC file with Apple Music metadata by track ID.

    Args:
        flac_path: Path to the FLAC file to tag
        track_id: Apple Music track ID
    """
    if not validate_flac_file(flac_path):
        console.print(f"❌ Invalid FLAC file: {flac_path}", style="red")
        raise typer.Exit(1)

    async def tag_process():
        async with AppleAPI() as apple:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Looking up track on Apple Music...", total=None)

                # Try to get track by ID using iTunes lookup
                session = await apple._get_session()
                params = {"id": track_id}

                async with session.get(f"{apple.ITUNES_BASE_URL}/lookup", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])

                        if results:
                            metadata = results[0]
                            progress.update(task, description="Applying tags to FLAC file...")
                            success = await apply_apple_tags(flac_path, metadata)

                            if success:
                                console.print(f"✅ Successfully tagged: {Path(flac_path).name}", style="green")
                                console.print(f"   Title: {metadata.get('trackName', 'Unknown')}")
                                console.print(f"   Artist: {metadata.get('artistName', 'Unknown')}")
                                console.print(f"   Album: {metadata.get('collectionName', 'Unknown')}")
                            else:
                                console.print(f"❌ Failed to apply tags", style="red")
                                raise typer.Exit(1)
                        else:
                            console.print(f"❌ No track found with ID: {track_id}", style="red")
                            raise typer.Exit(1)
                    else:
                        console.print(f"❌ Apple Music API error: {response.status}", style="red")
                        raise typer.Exit(1)

    asyncio.run(tag_process())
