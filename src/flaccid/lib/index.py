import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from mutagen.flac import FLAC
from ..shared.config import config

console = Console()
app = typer.Typer(help="Build or query the music library database.")

def get_db_path() -> Path:
    """Get the database file path."""
    db_dir = Path(config.get("FLACCID_DB_DIR", "~/.flaccid/db")).expanduser()
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "flaccid.db"

def init_database():
    """Initialize the database with required tables."""
    db_path = get_db_path()

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Create tracks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_mtime REAL,
                title TEXT,
                artist TEXT,
                album TEXT,
                album_artist TEXT,
                date TEXT,
                genre TEXT,
                track_number TEXT,
                disc_number TEXT,
                duration REAL,
                sample_rate INTEGER,
                bits_per_sample INTEGER,
                channels INTEGER,
                bitrate INTEGER,
                isrc TEXT,
                metadata_json TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for faster searching
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON tracks(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artist ON tracks(artist)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_album ON tracks(album)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_genre ON tracks(genre)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_isrc ON tracks(isrc)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON tracks(file_path)")

        conn.commit()

def extract_track_metadata(file_path: Path) -> dict:
    """Extract metadata from a FLAC file."""
    try:
        audio = FLAC(str(file_path))
        file_stats = file_path.stat()

        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_stats.st_size,
            'file_mtime': file_stats.st_mtime,
            'title': audio.get('TITLE', [''])[0],
            'artist': audio.get('ARTIST', [''])[0],
            'album': audio.get('ALBUM', [''])[0],
            'album_artist': audio.get('ALBUMARTIST', [''])[0] or audio.get('ARTIST', [''])[0],
            'date': audio.get('DATE', [''])[0],
            'genre': audio.get('GENRE', [''])[0],
            'track_number': audio.get('TRACKNUMBER', [''])[0],
            'disc_number': audio.get('DISCNUMBER', [''])[0],
            'duration': getattr(audio.info, 'length', 0),
            'sample_rate': getattr(audio.info, 'sample_rate', 0),
            'bits_per_sample': getattr(audio.info, 'bits_per_sample', 0),
            'channels': getattr(audio.info, 'channels', 0),
            'bitrate': getattr(audio.info, 'bitrate', 0),
            'isrc': audio.get('ISRC', [''])[0],
            'metadata_json': json.dumps(dict(audio))
        }

        return metadata
    except Exception as e:
        console.print(f"❌ Error reading {file_path}: {e}", style="red")
        return None

def add_track_to_db(metadata: dict):
    """Add or update a track in the database."""
    db_path = get_db_path()

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Check if track exists and if file has been modified
        cursor.execute(
            "SELECT file_mtime FROM tracks WHERE file_path = ?",
            (metadata['file_path'],)
        )
        existing = cursor.fetchone()

        if existing and existing[0] >= metadata['file_mtime']:
            # File hasn't changed, skip update
            return False

        # Insert or update track
        cursor.execute("""
            INSERT OR REPLACE INTO tracks (
                file_path, file_name, file_size, file_mtime,
                title, artist, album, album_artist, date, genre,
                track_number, disc_number, duration,
                sample_rate, bits_per_sample, channels, bitrate,
                isrc, metadata_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata['file_path'], metadata['file_name'], metadata['file_size'], metadata['file_mtime'],
            metadata['title'], metadata['artist'], metadata['album'], metadata['album_artist'],
            metadata['date'], metadata['genre'], metadata['track_number'], metadata['disc_number'],
            metadata['duration'], metadata['sample_rate'], metadata['bits_per_sample'],
            metadata['channels'], metadata['bitrate'], metadata['isrc'], metadata['metadata_json'],
            datetime.now().isoformat()
        ))

        conn.commit()
        return True

@app.command()
def build(path: str = typer.Option(".", help="Path to scan for FLAC files"),
          recursive: bool = typer.Option(True, "--recursive", "-r", help="Scan recursively")):
    """
    Build the music library database from scanned files.
    """
    scan_path = Path(path).expanduser().resolve()

    if not scan_path.exists():
        console.print(f"❌ Path not found: {path}", style="red")
        raise typer.Exit(1)

    console.print(f"🔨 Building music library database from: {scan_path}")

    # Initialize database
    init_database()

    # Find FLAC files
    if recursive:
        flac_files = list(scan_path.rglob("*.flac"))
    else:
        flac_files = list(scan_path.glob("*.flac"))

    if not flac_files:
        console.print("❌ No FLAC files found", style="red")
        return

    console.print(f"📁 Found {len(flac_files)} FLAC files")

    added_count = 0
    updated_count = 0
    error_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Indexing files...", total=len(flac_files))

        for flac_file in flac_files:
            metadata = extract_track_metadata(flac_file)
            if metadata:
                if add_track_to_db(metadata):
                    updated_count += 1
                else:
                    added_count += 1
            else:
                error_count += 1

            progress.advance(task)

    console.print(f"✅ Database build complete!")
    console.print(f"   Added/Updated: {updated_count} tracks")
    console.print(f"   Unchanged: {added_count} tracks")
    if error_count > 0:
        console.print(f"   Errors: {error_count} files", style="red")

@app.command()
def query(search_term: str):
    """
    Query the music library database.
    """
    db_path = get_db_path()

    if not db_path.exists():
        console.print("❌ Database not found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    console.print(f"🔍 Searching for: {search_term}")

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Search in multiple fields
        query = """
            SELECT title, artist, album, date, duration, file_name, file_path
            FROM tracks
            WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR file_name LIKE ?
            ORDER BY artist, album, CAST(track_number AS INTEGER)
            LIMIT 50
        """

        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))

        results = cursor.fetchall()

        if not results:
            console.print("❌ No matches found", style="red")
            return

        # Display results in a table
        table = Table(title=f"Search Results for '{search_term}'")
        table.add_column("Title", style="green")
        table.add_column("Artist", style="magenta")
        table.add_column("Album", style="blue")
        table.add_column("Year", style="yellow")
        table.add_column("Duration", style="cyan")
        table.add_column("File", style="dim")

        for row in results:
            title, artist, album, date, duration, file_name, file_path = row
            duration_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration else "Unknown"
            table.add_row(
                title or "Unknown",
                artist or "Unknown",
                album or "Unknown",
                date or "Unknown",
                duration_str,
                file_name
            )

        console.print(table)
        console.print(f"Found {len(results)} matches")

@app.command()
def stats():
    """
    Show music library statistics.
    """
    db_path = get_db_path()

    if not db_path.exists():
        console.print("❌ Database not found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    console.print("📊 Music Library Statistics")

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Total tracks
        cursor.execute("SELECT COUNT(*) FROM tracks")
        total_tracks = cursor.fetchone()[0]

        # Total albums
        cursor.execute("SELECT COUNT(DISTINCT album) FROM tracks WHERE album != ''")
        total_albums = cursor.fetchone()[0]

        # Total artists
        cursor.execute("SELECT COUNT(DISTINCT artist) FROM tracks WHERE artist != ''")
        total_artists = cursor.fetchone()[0]

        # Total duration
        cursor.execute("SELECT SUM(duration) FROM tracks")
        total_duration = cursor.fetchone()[0] or 0

        # Total file size
        cursor.execute("SELECT SUM(file_size) FROM tracks")
        total_size = cursor.fetchone()[0] or 0

        # Quality distribution
        cursor.execute("""
            SELECT sample_rate, bits_per_sample, COUNT(*)
            FROM tracks
            WHERE sample_rate > 0 AND bits_per_sample > 0
            GROUP BY sample_rate, bits_per_sample
            ORDER BY COUNT(*) DESC
        """)
        quality_stats = cursor.fetchall()

        # Top artists
        cursor.execute("""
            SELECT artist, COUNT(*) as track_count
            FROM tracks
            WHERE artist != ''
            GROUP BY artist
            ORDER BY track_count DESC
            LIMIT 10
        """)
        top_artists = cursor.fetchall()

        # Display statistics
        console.print(f"  Total tracks: {total_tracks}")
        console.print(f"  Total albums: {total_albums}")
        console.print(f"  Total artists: {total_artists}")
        console.print(f"  Total duration: {total_duration/3600:.1f} hours")
        console.print(f"  Total size: {total_size/(1024**3):.1f} GB")

        if quality_stats:
            console.print("\n🎵 Quality Distribution:")
            for sample_rate, bits_per_sample, count in quality_stats:
                console.print(f"  {sample_rate}Hz/{bits_per_sample}bit: {count} files")

        if top_artists:
            console.print("\n🎤 Top Artists:")
            for artist, count in top_artists:
                console.print(f"  {artist}: {count} tracks")

@app.command()
def remove_missing():
    """
    Remove tracks from database where files no longer exist.
    """
    db_path = get_db_path()

    if not db_path.exists():
        console.print("❌ Database not found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    console.print("🧹 Removing missing files from database...")

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Get all file paths
        cursor.execute("SELECT file_path FROM tracks")
        all_files = cursor.fetchall()

        missing_files = []
        for (file_path,) in all_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if not missing_files:
            console.print("✅ No missing files found")
            return

        console.print(f"🗑️  Found {len(missing_files)} missing files")

        if typer.confirm("Remove these files from the database?"):
            for file_path in missing_files:
                cursor.execute("DELETE FROM tracks WHERE file_path = ?", (file_path,))

            conn.commit()
            console.print(f"✅ Removed {len(missing_files)} missing files from database")
        else:
            console.print("❌ Cleanup cancelled")

if __name__ == "__main__":
    app()
