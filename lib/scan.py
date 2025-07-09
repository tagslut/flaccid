# mypy: ignore-errors
import hashlib
import json
from datetime import datetime
from pathlib import Path

import typer
from mutagen.flac import FLAC
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich.tree import Tree

console = Console()
app = typer.Typer(help="Scan FLAC files and extract metadata.")


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file for duplicate detection."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_flac_metadata(file_path: Path) -> dict:
    """Extract comprehensive metadata from FLAC file."""
    try:
        audio = FLAC(str(file_path))

        # File info
        info = {
            "path": str(file_path),
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "hash": get_file_hash(file_path),
        }

        # Audio properties
        if audio.info:
            info.update(
                {
                    "length": audio.info.length,
                    "bitrate": getattr(audio.info, "bitrate", 0),
                    "sample_rate": getattr(audio.info, "sample_rate", 0),
                    "channels": getattr(audio.info, "channels", 0),
                    "bits_per_sample": getattr(audio.info, "bits_per_sample", 0),
                }
            )

        # Common tags
        tag_mapping = {
            "title": ["TITLE", "title"],
            "artist": ["ARTIST", "artist"],
            "album": ["ALBUM", "album"],
            "albumartist": ["ALBUMARTIST", "albumartist"],
            "date": ["DATE", "date", "YEAR", "year"],
            "genre": ["GENRE", "genre"],
            "track": ["TRACKNUMBER", "tracknumber"],
            "disc": ["DISCNUMBER", "discnumber"],
            "composer": ["COMPOSER", "composer"],
            "performer": ["PERFORMER", "performer"],
            "label": ["LABEL", "label", "ORGANIZATION", "organization"],
            "isrc": ["ISRC", "isrc"],
            "barcode": ["BARCODE", "barcode"],
            "catalog": ["CATALOGNUMBER", "catalognumber"],
            "comment": ["COMMENT", "comment"],
            "copyright": ["COPYRIGHT", "copyright"],
        }

        tags = {}
        for key, possible_tags in tag_mapping.items():
            for tag in possible_tags:
                if tag in audio:
                    tags[key] = audio[tag][0] if audio[tag] else ""
                    break
            if key not in tags:
                tags[key] = ""

        # Additional metadata
        info["tags"] = tags

        # Custom tags (FLACCID specific)
        custom_tags = {}
        for key, value in audio.items():
            if key.startswith("FLACCID_"):
                custom_tags[key] = value[0] if value else ""

        if custom_tags:
            info["custom_tags"] = custom_tags

        return info

    except Exception as e:
        return {"path": str(file_path), "filename": file_path.name, "error": str(e)}


def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS format."""
    if seconds <= 0:
        return "0:00"

    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"


def format_size(bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"


@app.command("file")
def scan_file(
    file_path: str,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed metadata"
    ),
):
    """
    Scan a single FLAC file and display its metadata.

    Args:
        file_path: Path to the FLAC file
        verbose: Show detailed metadata including custom tags
    """
    file = Path(file_path).expanduser()

    if not file.exists():
        console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)

    if not file.suffix.lower() == ".flac":
        console.print(f"❌ Not a FLAC file: {file_path}", style="red")
        raise typer.Exit(1)

    console.print(f"📁 Scanning: {file.name}")

    metadata = extract_flac_metadata(file)

    if "error" in metadata:
        console.print(f"❌ Error reading file: {metadata['error']}", style="red")
        return

    # Create table for display
    table = Table(title=f"FLAC Metadata: {file.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    # File info
    table.add_row("Path", metadata["path"])
    table.add_row("Size", format_size(metadata["size"]))
    table.add_row("Modified", metadata["modified"][:19])  # Remove milliseconds

    # Audio properties
    if "length" in metadata:
        table.add_row("Duration", format_duration(metadata["length"]))
        table.add_row("Sample Rate", f"{metadata.get('sample_rate', 0)} Hz")
        table.add_row("Channels", str(metadata.get("channels", 0)))
        table.add_row("Bits per Sample", str(metadata.get("bits_per_sample", 0)))
        table.add_row("Bitrate", f"{metadata.get('bitrate', 0)} kbps")

    # Tags
    tags = metadata.get("tags", {})
    if tags:
        table.add_row("", "")  # Separator
        table.add_row("Title", tags.get("title", ""))
        table.add_row("Artist", tags.get("artist", ""))
        table.add_row("Album", tags.get("album", ""))
        table.add_row("Album Artist", tags.get("albumartist", ""))
        table.add_row("Date", tags.get("date", ""))
        table.add_row("Genre", tags.get("genre", ""))
        table.add_row("Track", tags.get("track", ""))
        table.add_row("Disc", tags.get("disc", ""))
        table.add_row("Composer", tags.get("composer", ""))
        table.add_row("Label", tags.get("label", ""))
        table.add_row("ISRC", tags.get("isrc", ""))

    # Custom tags if verbose
    if verbose and "custom_tags" in metadata:
        table.add_row("", "")  # Separator
        for key, value in metadata["custom_tags"].items():
            table.add_row(key, value)

    console.print(table)


@app.command("dir")
def scan_dir(
    directory: str,
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Scan subdirectories recursively"
    ),
):
    """
    Scan a directory and list FLAC files with basic metadata.

    Args:
        directory: Directory to scan
        recursive: Scan subdirectories recursively
    """
    folder = Path(directory).expanduser()

    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    if not folder.is_dir():
        console.print(f"❌ Not a directory: {directory}", style="red")
        raise typer.Exit(1)

    console.print(f"📁 Scanning: {folder}")

    # Find FLAC files
    if recursive:
        flac_files = list(folder.rglob("*.flac"))
    else:
        flac_files = list(folder.glob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {directory}", style="red")
        return

    console.print(f"🎵 Found {len(flac_files)} FLAC files")

    # Create table for results
    table = Table(title=f"FLAC Files in {folder.name}")
    table.add_column("File", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Artist", style="green")
    table.add_column("Album", style="yellow")
    table.add_column("Duration", style="blue")
    table.add_column("Size", style="magenta")

    for file_path in track(flac_files, description="Scanning files..."):
        metadata = extract_flac_metadata(file_path)

        if "error" in metadata:
            table.add_row(
                file_path.name, f"[red]Error: {metadata['error']}[/red]", "", "", "", ""
            )
            continue

        tags = metadata.get("tags", {})
        table.add_row(
            file_path.name,
            tags.get("title", "Unknown"),
            tags.get("artist", "Unknown"),
            tags.get("album", "Unknown"),
            format_duration(metadata.get("length", 0)),
            format_size(metadata.get("size", 0)),
        )

    console.print(table)


@app.command("tree")
def scan_tree(
    directory: str,
    show_tags: bool = typer.Option(
        False, "--tags", "-t", help="Show track tags in tree"
    ),
):
    """
    Display directory structure with FLAC files in a tree format.

    Args:
        directory: Directory to scan
        show_tags: Show track tags in the tree
    """
    folder = Path(directory).expanduser()

    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    def build_tree(path: Path, tree: Tree):
        """Recursively build tree structure."""
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

            for item in items:
                if item.is_dir():
                    # Add directory
                    dir_tree = tree.add(f"📁 {item.name}", style="bold blue")
                    build_tree(item, dir_tree)
                elif item.suffix.lower() == ".flac":
                    # Add FLAC file
                    if show_tags:
                        metadata = extract_flac_metadata(item)
                        if "error" not in metadata:
                            tags = metadata.get("tags", {})
                            title = tags.get("title", "Unknown")
                            artist = tags.get("artist", "Unknown")
                            duration = format_duration(metadata.get("length", 0))

                            file_text = f"🎵 {item.name}"
                            if title != "Unknown":
                                file_text += f" - {title}"
                            if artist != "Unknown":
                                file_text += f" by {artist}"
                            file_text += f" ({duration})"

                            tree.add(file_text, style="green")
                        else:
                            tree.add(f"🎵 {item.name} [red](Error)[/red]", style="red")
                    else:
                        tree.add(f"🎵 {item.name}", style="green")
                else:
                    # Add other files
                    tree.add(f"📄 {item.name}", style="dim")
        except PermissionError:
            tree.add("[red]Permission denied[/red]", style="red")

    # Create root tree
    tree = Tree(f"📁 {folder.name}", style="bold blue")

    with console.status("Building tree..."):
        build_tree(folder, tree)

    console.print(tree)


@app.command("export")
def export_metadata(
    directory: str,
    output: str,
    format: str = typer.Option("json", help="Output format (json, csv)"),
):
    """
    Export FLAC metadata to a file.

    Args:
        directory: Directory to scan
        output: Output file path
        format: Output format (json or csv)
    """
    folder = Path(directory).expanduser()
    output_file = Path(output).expanduser()

    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    # Find all FLAC files
    flac_files = list(folder.rglob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {directory}", style="red")
        return

    console.print(f"🎵 Found {len(flac_files)} FLAC files")

    # Extract metadata
    metadata_list = []

    for file_path in track(flac_files, description="Extracting metadata..."):
        metadata = extract_flac_metadata(file_path)
        metadata_list.append(metadata)

    # Export data
    if format.lower() == "json":
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)
        console.print(f"✅ Exported to JSON: {output_file}")

    elif format.lower() == "csv":
        import csv

        if not metadata_list:
            console.print("❌ No metadata to export", style="red")
            return

        # Get all possible fields
        all_fields = set()
        for metadata in metadata_list:
            all_fields.update(metadata.keys())
            if "tags" in metadata:
                all_fields.update(f"tag_{k}" for k in metadata["tags"].keys())

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
            writer.writeheader()

            for metadata in metadata_list:
                row = {}
                for field in all_fields:
                    if field.startswith("tag_"):
                        tag_name = field[4:]  # Remove "tag_" prefix
                        row[field] = metadata.get("tags", {}).get(tag_name, "")
                    else:
                        row[field] = metadata.get(field, "")
                writer.writerow(row)

        console.print(f"✅ Exported to CSV: {output_file}")

    else:
        console.print(f"❌ Unsupported format: {format}", style="red")
        raise typer.Exit(1)


@app.command("duplicates")
def find_duplicates(
    directory: str,
    by: str = typer.Option("hash", help="Find duplicates by: hash, title, filename"),
):
    """
    Find duplicate FLAC files in a directory.

    Args:
        directory: Directory to scan
        by: Method to detect duplicates (hash, title, filename)
    """
    folder = Path(directory).expanduser()

    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    # Find all FLAC files
    flac_files = list(folder.rglob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {directory}", style="red")
        return

    console.print(f"🎵 Scanning {len(flac_files)} FLAC files for duplicates...")

    # Group files by the specified criteria
    groups = {}

    for file_path in track(flac_files, description="Analyzing files..."):
        if by == "hash":
            try:
                key = get_file_hash(file_path)
            except Exception as e:
                console.print(f"❌ Error hashing {file_path}: {e}", style="red")
                continue
        elif by == "filename":
            key = file_path.name.lower()
        elif by == "title":
            metadata = extract_flac_metadata(file_path)
            if "error" in metadata:
                continue
            key = metadata.get("tags", {}).get("title", "").lower()
            if not key:
                continue
        else:
            console.print(f"❌ Invalid comparison method: {by}", style="red")
            return

        if key not in groups:
            groups[key] = []
        groups[key].append(file_path)

    # Find duplicates
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    if not duplicates:
        console.print("✅ No duplicates found!", style="green")
        return

    console.print(f"🔍 Found {len(duplicates)} groups of duplicates:")

    for i, (key, files) in enumerate(duplicates.items(), 1):
        console.print(f"\n[bold]Group {i}[/bold] ({by}: {key}):")

        for file_path in files:
            metadata = extract_flac_metadata(file_path)
            if "error" not in metadata:
                tags = metadata.get("tags", {})
                size = format_size(metadata.get("size", 0))
                duration = format_duration(metadata.get("length", 0))

                console.print(f"  📄 {file_path}")
                console.print(f"     Title: {tags.get('title', 'Unknown')}")
                console.print(f"     Artist: {tags.get('artist', 'Unknown')}")
                console.print(f"     Size: {size}, Duration: {duration}")
            else:
                console.print(f"  📄 {file_path} [red](Error)[/red]")


@app.command("stats")
def library_stats(directory: str):
    """
    Display statistics about your FLAC library.

    Args:
        directory: Directory to analyze
    """
    folder = Path(directory).expanduser()

    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    # Find all FLAC files
    flac_files = list(folder.rglob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {directory}", style="red")
        return

    console.print(f"📊 Analyzing {len(flac_files)} FLAC files...")

    # Collect statistics
    stats = {
        "total_files": len(flac_files),
        "total_size": 0,
        "total_duration": 0,
        "artists": set(),
        "albums": set(),
        "genres": set(),
        "years": set(),
        "sample_rates": {},
        "bit_depths": {},
        "channels": {},
        "errors": 0,
    }

    for file_path in track(flac_files, description="Analyzing files..."):
        metadata = extract_flac_metadata(file_path)

        if "error" in metadata:
            stats["errors"] += 1
            continue

        # File stats
        stats["total_size"] += metadata.get("size", 0)
        stats["total_duration"] += metadata.get("length", 0)

        # Audio properties
        sample_rate = metadata.get("sample_rate", 0)
        if sample_rate:
            stats["sample_rates"][sample_rate] = (
                stats["sample_rates"].get(sample_rate, 0) + 1
            )

        bit_depth = metadata.get("bits_per_sample", 0)
        if bit_depth:
            stats["bit_depths"][bit_depth] = stats["bit_depths"].get(bit_depth, 0) + 1

        channels = metadata.get("channels", 0)
        if channels:
            stats["channels"][channels] = stats["channels"].get(channels, 0) + 1

        # Tags
        tags = metadata.get("tags", {})
        if tags.get("artist"):
            stats["artists"].add(tags["artist"])
        if tags.get("album"):
            stats["albums"].add(tags["album"])
        if tags.get("genre"):
            stats["genres"].add(tags["genre"])
        if tags.get("date"):
            # Extract year from date
            year = tags["date"][:4] if len(tags["date"]) >= 4 else tags["date"]
            if year.isdigit():
                stats["years"].add(year)

    # Display statistics
    table = Table(title="Library Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    # Basic stats
    table.add_row("Total Files", str(stats["total_files"]))
    table.add_row("Total Size", format_size(stats["total_size"]))
    table.add_row("Total Duration", format_duration(stats["total_duration"]))
    table.add_row("Unique Artists", str(len(stats["artists"])))
    table.add_row("Unique Albums", str(len(stats["albums"])))
    table.add_row("Unique Genres", str(len(stats["genres"])))
    table.add_row(
        "Year Range",
        (
            f"{min(stats['years'])} - {max(stats['years'])}"
            if stats["years"]
            else "Unknown"
        ),
    )

    # Audio quality
    if stats["sample_rates"]:
        most_common_sr = max(stats["sample_rates"], key=stats["sample_rates"].get)
        table.add_row("Most Common Sample Rate", f"{most_common_sr} Hz")

    if stats["bit_depths"]:
        most_common_bd = max(stats["bit_depths"], key=stats["bit_depths"].get)
        table.add_row("Most Common Bit Depth", f"{most_common_bd} bits")

    if stats["channels"]:
        most_common_ch = max(stats["channels"], key=stats["channels"].get)
        table.add_row("Most Common Channels", str(most_common_ch))

    if stats["errors"]:
        table.add_row("Files with Errors", str(stats["errors"]))

    console.print(table)

    # Show top artists if we have data
    if stats["artists"]:
        console.print("\n[bold]Sample Artists:[/bold]")
        for artist in sorted(list(stats["artists"]))[:10]:
            console.print(f"  • {artist}")

    # Show top genres if we have data
    if stats["genres"]:
        console.print("\n[bold]Sample Genres:[/bold]")
        for genre in sorted(list(stats["genres"]))[:10]:
            console.print(f"  • {genre}")
