import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError
import os

console = Console()
app = typer.Typer(help="Scan directories and extract metadata.")

def get_flac_info(file_path: Path) -> dict:
    """Extract basic information from a FLAC file."""
    try:
        audio = FLAC(str(file_path))

        # Get file size
        file_size = file_path.stat().st_size

        # Get basic metadata
        info = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 1),
            'title': audio.get('TITLE', ['Unknown'])[0],
            'artist': audio.get('ARTIST', ['Unknown'])[0],
            'album': audio.get('ALBUM', ['Unknown'])[0],
            'date': audio.get('DATE', ['Unknown'])[0],
            'genre': audio.get('GENRE', ['Unknown'])[0],
            'track_number': audio.get('TRACKNUMBER', ['Unknown'])[0],
            'sample_rate': getattr(audio.info, 'sample_rate', 'Unknown'),
            'bits_per_sample': getattr(audio.info, 'bits_per_sample', 'Unknown'),
            'channels': getattr(audio.info, 'channels', 'Unknown'),
            'length': getattr(audio.info, 'length', 0),
            'bitrate': getattr(audio.info, 'bitrate', 'Unknown'),
        }

        return info
    except Exception as e:
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'error': str(e)
        }

def scan_directory_for_flac(path: Path, recursive: bool = False) -> list:
    """Scan directory for FLAC files and return list of file info."""
    files = []

    if recursive:
        flac_files = list(path.rglob("*.flac"))
    else:
        flac_files = list(path.glob("*.flac"))

    if not flac_files:
        return []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Scanning FLAC files...", total=len(flac_files))

        for flac_file in flac_files:
            info = get_flac_info(flac_file)
            files.append(info)
            progress.advance(task)

    return files

@app.command()
def directory(path: str):
    """
    Scan a directory for FLAC files and extract metadata.
    """
    scan_path = Path(path)
    if not scan_path.exists():
        console.print(f"❌ Directory not found: {path}", style="red")
        raise typer.Exit(1)

    console.print(f"📁 Scanning directory: {path}")

    files = scan_directory_for_flac(scan_path, recursive=False)

    if not files:
        console.print("❌ No FLAC files found in directory", style="red")
        return

    # Create summary table
    table = Table(title=f"FLAC Files in {scan_path.name}")
    table.add_column("File", style="cyan")
    table.add_column("Artist", style="magenta")
    table.add_column("Title", style="green")
    table.add_column("Album", style="blue")
    table.add_column("Size (MB)", justify="right")
    table.add_column("Quality", style="yellow")

    total_size = 0
    for file_info in files:
        if "error" in file_info:
            table.add_row(
                file_info["file_name"],
                "[red]ERROR[/red]",
                file_info["error"],
                "",
                "",
                "",
            )
        else:
            quality = f"{file_info['sample_rate']}Hz/{file_info['bits_per_sample']}bit"
            table.add_row(
                file_info["file_name"],
                file_info["artist"],
                file_info["title"],
                file_info["album"],
                str(file_info["file_size_mb"]),
                quality,
            )
            total_size += file_info["file_size_mb"]

    console.print(table)
    console.print(f"\n📊 Summary: {len(files)} FLAC files, {total_size:.1f} MB total")

@app.command()
def recursive(path: str):
    """
    Recursively scan directories for FLAC files.
    """
    scan_path = Path(path)
    if not scan_path.exists():
        console.print(f"❌ Directory not found: {path}", style="red")
        raise typer.Exit(1)

    console.print(f"📁 Recursively scanning: {path}")

    files = scan_directory_for_flac(scan_path, recursive=True)

    if not files:
        console.print("❌ No FLAC files found in directory tree", style="red")
        return

    # Group files by directory
    dir_groups = {}
    for file_info in files:
        dir_path = Path(file_info['file_path']).parent
        if dir_path not in dir_groups:
            dir_groups[dir_path] = []
        dir_groups[dir_path].append(file_info)

    # Show summary by directory
    for dir_path, dir_files in dir_groups.items():
        console.print(f"\n📁 {dir_path}")

        table = Table()
        table.add_column("File", style="cyan")
        table.add_column("Artist", style="magenta")
        table.add_column("Title", style="green")
        table.add_column("Size (MB)", justify="right")
        table.add_column("Quality", style="yellow")

        dir_size = 0
        for file_info in dir_files:
            if 'error' in file_info:
                table.add_row(file_info['file_name'], "[red]ERROR[/red]", file_info['error'], "", "")
            else:
                quality = f"{file_info['sample_rate']}Hz/{file_info['bits_per_sample']}bit"
                table.add_row(
                    file_info['file_name'],
                    file_info['artist'],
                    file_info['title'],
                    str(file_info['file_size_mb']),
                    quality
                )
                dir_size += file_info['file_size_mb']

        console.print(table)
        console.print(f"   {len(dir_files)} files, {dir_size:.1f} MB")

    total_size = sum(f['file_size_mb'] for f in files if 'error' not in f)
    console.print(f"\n� Total: {len(files)} FLAC files in {len(dir_groups)} directories, {total_size:.1f} MB")

@app.command()
def stats(path: str, recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan recursively")):
    """
    Generate detailed statistics about FLAC files.
    """
    scan_path = Path(path)
    if not scan_path.exists():
        console.print(f"❌ Directory not found: {path}", style="red")
        raise typer.Exit(1)

    console.print(f"📊 Generating statistics for: {path}")

    files = scan_directory_for_flac(scan_path, recursive=recursive)

    if not files:
        console.print("❌ No FLAC files found", style="red")
        return

    # Filter out files with errors
    valid_files = [f for f in files if 'error' not in f]
    error_files = [f for f in files if 'error' in f]

    if not valid_files:
        console.print("❌ No valid FLAC files found", style="red")
        return

    # Calculate statistics
    total_size = sum(f['file_size_mb'] for f in valid_files)
    total_duration = sum(f['length'] for f in valid_files)

    # Quality statistics
    quality_stats = {}
    for f in valid_files:
        quality = f"{f['sample_rate']}Hz/{f['bits_per_sample']}bit"
        if quality not in quality_stats:
            quality_stats[quality] = 0
        quality_stats[quality] += 1

    # Artist statistics
    artist_stats = {}
    for f in valid_files:
        artist = f['artist']
        if artist not in artist_stats:
            artist_stats[artist] = 0
        artist_stats[artist] += 1

    # Display statistics
    console.print("\n📈 FLAC Collection Statistics")
    console.print(f"Total files: {len(valid_files)}")
    console.print(f"Total size: {total_size:.1f} MB ({total_size/1024:.1f} GB)")
    console.print(f"Total duration: {total_duration/3600:.1f} hours")
    console.print(f"Average file size: {total_size/len(valid_files):.1f} MB")

    if error_files:
        console.print(f"Files with errors: {len(error_files)}", style="red")

    # Quality distribution
    if quality_stats:
        console.print("\n🎵 Quality Distribution:")
        for quality, count in sorted(quality_stats.items()):
            percentage = (count / len(valid_files)) * 100
            console.print(f"  {quality}: {count} files ({percentage:.1f}%)")

    # Top artists
    if artist_stats:
        console.print("\n🎤 Top Artists:")
        sorted_artists = sorted(artist_stats.items(), key=lambda x: x[1], reverse=True)
        for artist, count in sorted_artists[:10]:
            console.print(f"  {artist}: {count} files")

if __name__ == "__main__":
    app()
