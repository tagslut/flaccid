import typer
import sqlite3
from pathlib import Path
from mutagen.flac import FLAC
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, track
from datetime import datetime
import json
import hashlib
from typing import List, Dict, Optional, Tuple

console = Console()
app = typer.Typer(help="Index FLAC files into a local SQLite database.")

# Default database location
DEFAULT_DB_PATH = Path.home() / ".flaccid" / "library.db"

class LibraryIndexer:
    """Manages the FLAC library database."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")

        # Create tables
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                directory TEXT NOT NULL,
                size INTEGER NOT NULL,
                hash TEXT NOT NULL,
                modified TEXT NOT NULL,
                indexed TEXT NOT NULL,
                length REAL,
                bitrate INTEGER,
                sample_rate INTEGER,
                channels INTEGER,
                bits_per_sample INTEGER
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                title TEXT,
                artist TEXT,
                album TEXT,
                albumartist TEXT,
                date TEXT,
                genre TEXT,
                track TEXT,
                disc TEXT,
                composer TEXT,
                performer TEXT,
                label TEXT,
                isrc TEXT,
                barcode TEXT,
                catalog TEXT,
                comment TEXT,
                copyright TEXT,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS custom_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                tag_value TEXT,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                date TEXT,
                genre TEXT,
                label TEXT,
                barcode TEXT,
                catalog TEXT,
                total_tracks INTEGER,
                total_discs INTEGER,
                created TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                album_count INTEGER DEFAULT 0,
                track_count INTEGER DEFAULT 0,
                created TEXT NOT NULL
            );

            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
            CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash);
            CREATE INDEX IF NOT EXISTS idx_tags_file_id ON tags(file_id);
            CREATE INDEX IF NOT EXISTS idx_tags_artist ON tags(artist);
            CREATE INDEX IF NOT EXISTS idx_tags_album ON tags(album);
            CREATE INDEX IF NOT EXISTS idx_tags_title ON tags(title);
            CREATE INDEX IF NOT EXISTS idx_custom_tags_file_id ON custom_tags(file_id);
            CREATE INDEX IF NOT EXISTS idx_custom_tags_name ON custom_tags(tag_name);
        """)

        conn.close()

    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def extract_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from FLAC file."""
        try:
            audio = FLAC(str(file_path))
            stat = file_path.stat()

            metadata = {
                "file_info": {
                    "path": str(file_path),
                    "filename": file_path.name,
                    "directory": str(file_path.parent),
                    "size": stat.st_size,
                    "hash": self.get_file_hash(file_path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "indexed": datetime.now().isoformat(),
                }
            }

            # Audio properties
            if audio.info:
                metadata["audio_info"] = {
                    "length": audio.info.length,
                    "bitrate": getattr(audio.info, 'bitrate', 0),
                    "sample_rate": getattr(audio.info, 'sample_rate', 0),
                    "channels": getattr(audio.info, 'channels', 0),
                    "bits_per_sample": getattr(audio.info, 'bits_per_sample', 0),
                }

            # Standard tags
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

            metadata["tags"] = tags

            # Custom tags
            custom_tags = {}
            for key, value in audio.items():
                if key.startswith("FLACCID_") or key not in [tag for tags in tag_mapping.values() for tag in tags]:
                    custom_tags[key] = value[0] if value else ""

            metadata["custom_tags"] = custom_tags

            return metadata

        except Exception as e:
            return {"error": str(e)}

    def add_file(self, file_path: Path) -> bool:
        """Add a file to the database."""
        metadata = self.extract_metadata(file_path)

        if "error" in metadata:
            console.print(f"❌ Error processing {file_path}: {metadata['error']}", style="red")
            return False

        conn = sqlite3.connect(self.db_path)

        try:
            # Insert file info
            file_info = metadata["file_info"]
            audio_info = metadata.get("audio_info", {})

            cursor = conn.execute("""
                INSERT OR REPLACE INTO files
                (path, filename, directory, size, hash, modified, indexed,
                 length, bitrate, sample_rate, channels, bits_per_sample)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_info["path"], file_info["filename"], file_info["directory"],
                file_info["size"], file_info["hash"], file_info["modified"], file_info["indexed"],
                audio_info.get("length"), audio_info.get("bitrate"), audio_info.get("sample_rate"),
                audio_info.get("channels"), audio_info.get("bits_per_sample")
            ))

            file_id = cursor.lastrowid

            # Delete existing tags for this file
            conn.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
            conn.execute("DELETE FROM custom_tags WHERE file_id = ?", (file_id,))

            # Insert tags
            tags = metadata.get("tags", {})
            conn.execute("""
                INSERT INTO tags
                (file_id, title, artist, album, albumartist, date, genre, track, disc,
                 composer, performer, label, isrc, barcode, catalog, comment, copyright)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id, tags.get("title"), tags.get("artist"), tags.get("album"),
                tags.get("albumartist"), tags.get("date"), tags.get("genre"),
                tags.get("track"), tags.get("disc"), tags.get("composer"),
                tags.get("performer"), tags.get("label"), tags.get("isrc"),
                tags.get("barcode"), tags.get("catalog"), tags.get("comment"),
                tags.get("copyright")
            ))

            # Insert custom tags
            custom_tags = metadata.get("custom_tags", {})
            for tag_name, tag_value in custom_tags.items():
                if tag_value:  # Only insert non-empty values
                    conn.execute("""
                        INSERT INTO custom_tags (file_id, tag_name, tag_value)
                        VALUES (?, ?, ?)
                    """, (file_id, tag_name, tag_value))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            console.print(f"❌ Database error: {e}", style="red")
            return False

        finally:
            conn.close()

    def remove_file(self, file_path: str) -> bool:
        """Remove a file from the database."""
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.execute("DELETE FROM files WHERE path = ?", (file_path,))
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def update_aggregates(self):
        """Update aggregate tables (albums, artists)."""
        conn = sqlite3.connect(self.db_path)

        try:
            # Clear existing aggregates
            conn.execute("DELETE FROM albums")
            conn.execute("DELETE FROM artists")

            # Rebuild albums
            conn.execute("""
                INSERT INTO albums (title, artist, date, genre, label, barcode, catalog, total_tracks, total_discs, created)
                SELECT
                    t.album,
                    t.albumartist,
                    t.date,
                    t.genre,
                    t.label,
                    t.barcode,
                    t.catalog,
                    COUNT(*) as total_tracks,
                    COUNT(DISTINCT t.disc) as total_discs,
                    datetime('now') as created
                FROM tags t
                WHERE t.album IS NOT NULL AND t.album != ''
                GROUP BY t.album, t.albumartist, t.date, t.genre, t.label, t.barcode, t.catalog
            """)

            # Rebuild artists
            conn.execute("""
                INSERT INTO artists (name, album_count, track_count, created)
                SELECT
                    t.artist,
                    COUNT(DISTINCT t.album) as album_count,
                    COUNT(*) as track_count,
                    datetime('now') as created
                FROM tags t
                WHERE t.artist IS NOT NULL AND t.artist != ''
                GROUP BY t.artist
            """)

            conn.commit()

        finally:
            conn.close()

def get_indexer(db_path: str = None) -> LibraryIndexer:
    """Get a LibraryIndexer instance."""
    if db_path:
        return LibraryIndexer(Path(db_path))
    return LibraryIndexer()

@app.command("build")
def build_index(music_dir: str, db_path: str = None, force: bool = typer.Option(False, "--force", "-f", help="Force rebuild, ignoring existing entries")):
    """
    Create or refresh the index of your music files.

    Args:
        music_dir: Directory containing FLAC files
        db_path: Custom database path (optional)
        force: Force rebuild, ignoring existing entries
    """
    music_path = Path(music_dir).expanduser()

    if not music_path.exists():
        console.print(f"❌ Directory not found: {music_dir}", style="red")
        raise typer.Exit(1)

    indexer = get_indexer(db_path)

    # Find all FLAC files
    flac_files = list(music_path.rglob("*.flac"))

    if not flac_files:
        console.print(f"❌ No FLAC files found in: {music_dir}", style="red")
        return

    console.print(f"🎵 Found {len(flac_files)} FLAC files")

    if not force:
        # Check which files are already indexed
        conn = sqlite3.connect(indexer.db_path)
        existing_files = set()

        for row in conn.execute("SELECT path, hash FROM files"):
            existing_files.add((row[0], row[1]))

        conn.close()

        # Filter out files that haven't changed
        new_files = []
        for file_path in flac_files:
            try:
                file_hash = indexer.get_file_hash(file_path)
                if (str(file_path), file_hash) not in existing_files:
                    new_files.append(file_path)
            except Exception:
                new_files.append(file_path)  # Re-index if hash fails

        if new_files:
            console.print(f"📁 {len(new_files)} new or changed files to index")
            flac_files = new_files
        else:
            console.print("✅ All files are up to date")
            return

    # Index files
    success_count = 0
    error_count = 0

    for file_path in track(flac_files, description="Indexing files..."):
        if indexer.add_file(file_path):
            success_count += 1
        else:
            error_count += 1

    # Update aggregates
    console.print("🔄 Updating aggregates...")
    indexer.update_aggregates()

    console.print(f"✅ Indexing complete!")
    console.print(f"   Successfully indexed: {success_count}")
    if error_count > 0:
        console.print(f"   Errors: {error_count}", style="red")

@app.command("search")
def search_library(query: str, db_path: str = None, limit: int = typer.Option(20, help="Maximum results to show")):
    """
    Search the indexed library.

    Args:
        query: Search query
        db_path: Custom database path (optional)
        limit: Maximum results to show
    """
    indexer = get_indexer(db_path)

    if not indexer.db_path.exists():
        console.print("❌ No index found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    conn = sqlite3.connect(indexer.db_path)

    # Search in tags
    search_query = f"%{query}%"

    results = conn.execute("""
        SELECT f.path, f.filename, t.title, t.artist, t.album, t.date, t.genre, f.length
        FROM files f
        JOIN tags t ON f.id = t.file_id
        WHERE t.title LIKE ? OR t.artist LIKE ? OR t.album LIKE ? OR t.genre LIKE ?
        ORDER BY t.artist, t.album, t.track
        LIMIT ?
    """, (search_query, search_query, search_query, search_query, limit)).fetchall()

    conn.close()

    if not results:
        console.print(f"❌ No results found for: {query}", style="red")
        return

    console.print(f"🔍 Found {len(results)} results for: {query}")

    # Display results
    table = Table(title="Search Results")
    table.add_column("Title", style="cyan")
    table.add_column("Artist", style="green")
    table.add_column("Album", style="yellow")
    table.add_column("Year", style="blue")
    table.add_column("Genre", style="magenta")
    table.add_column("Duration", style="white")

    for result in results:
        path, filename, title, artist, album, date, genre, length = result

        # Format duration
        duration = ""
        if length:
            minutes = int(length // 60)
            seconds = int(length % 60)
            duration = f"{minutes}:{seconds:02d}"

        table.add_row(
            title or "Unknown",
            artist or "Unknown",
            album or "Unknown",
            date[:4] if date and len(date) >= 4 else "Unknown",
            genre or "Unknown",
            duration
        )

    console.print(table)

@app.command("stats")
def index_stats(db_path: str = None):
    """
    Show statistics about the indexed library.

    Args:
        db_path: Custom database path (optional)
    """
    indexer = get_indexer(db_path)

    if not indexer.db_path.exists():
        console.print("❌ No index found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    conn = sqlite3.connect(indexer.db_path)

    # Collect statistics
    stats = {}

    # Basic counts
    stats["total_files"] = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    stats["total_artists"] = conn.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    stats["total_albums"] = conn.execute("SELECT COUNT(*) FROM albums").fetchone()[0]

    # Size and duration
    size_duration = conn.execute("SELECT SUM(size), SUM(length) FROM files").fetchone()
    stats["total_size"] = size_duration[0] or 0
    stats["total_duration"] = size_duration[1] or 0

    # Audio quality stats
    stats["sample_rates"] = conn.execute("""
        SELECT sample_rate, COUNT(*)
        FROM files
        WHERE sample_rate IS NOT NULL
        GROUP BY sample_rate
        ORDER BY COUNT(*) DESC
    """).fetchall()

    stats["bit_depths"] = conn.execute("""
        SELECT bits_per_sample, COUNT(*)
        FROM files
        WHERE bits_per_sample IS NOT NULL
        GROUP BY bits_per_sample
        ORDER BY COUNT(*) DESC
    """).fetchall()

    # Top artists
    stats["top_artists"] = conn.execute("""
        SELECT name, track_count, album_count
        FROM artists
        ORDER BY track_count DESC
        LIMIT 10
    """).fetchall()

    # Top genres
    stats["top_genres"] = conn.execute("""
        SELECT genre, COUNT(*) as count
        FROM tags
        WHERE genre IS NOT NULL AND genre != ''
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    # Display statistics
    table = Table(title="Library Index Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Files", str(stats["total_files"]))
    table.add_row("Total Artists", str(stats["total_artists"]))
    table.add_row("Total Albums", str(stats["total_albums"]))

    # Format size
    size = stats["total_size"]
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            table.add_row("Total Size", f"{size:.1f}{unit}")
            break
        size /= 1024.0

    # Format duration
    duration = stats["total_duration"]
    if duration:
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        table.add_row("Total Duration", f"{hours}h {minutes}m")

    # Audio quality
    if stats["sample_rates"]:
        most_common_sr = stats["sample_rates"][0]
        table.add_row("Most Common Sample Rate", f"{most_common_sr[0]} Hz ({most_common_sr[1]} files)")

    if stats["bit_depths"]:
        most_common_bd = stats["bit_depths"][0]
        table.add_row("Most Common Bit Depth", f"{most_common_bd[0]} bits ({most_common_bd[1]} files)")

    console.print(table)

    # Top artists
    if stats["top_artists"]:
        console.print("\n[bold]Top Artists:[/bold]")
        artist_table = Table()
        artist_table.add_column("Artist", style="green")
        artist_table.add_column("Tracks", style="cyan")
        artist_table.add_column("Albums", style="yellow")

        for artist, tracks, albums in stats["top_artists"]:
            artist_table.add_row(artist, str(tracks), str(albums))

        console.print(artist_table)

    # Top genres
    if stats["top_genres"]:
        console.print("\n[bold]Top Genres:[/bold]")
        genre_table = Table()
        genre_table.add_column("Genre", style="magenta")
        genre_table.add_column("Tracks", style="cyan")

        for genre, count in stats["top_genres"]:
            genre_table.add_row(genre, str(count))

        console.print(genre_table)

@app.command("clean")
def clean_index(db_path: str = None, dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed without actually removing it")):
    """
    Remove entries for files that no longer exist.

    Args:
        db_path: Custom database path (optional)
        dry_run: Show what would be removed without actually removing it
    """
    indexer = get_indexer(db_path)

    if not indexer.db_path.exists():
        console.print("❌ No index found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    conn = sqlite3.connect(indexer.db_path)

    # Find files in database that don't exist on disk
    missing_files = []

    for row in conn.execute("SELECT id, path FROM files"):
        file_id, file_path = row
        if not Path(file_path).exists():
            missing_files.append((file_id, file_path))

    if not missing_files:
        console.print("✅ No missing files found in index.", style="green")
        conn.close()
        return

    console.print(f"🗑️  Found {len(missing_files)} missing files")

    if dry_run:
        console.print("\n[bold]Would remove:[/bold]")
        for file_id, file_path in missing_files:
            console.print(f"  📄 {file_path}")
        console.print(f"\n[yellow]Run without --dry-run to actually remove these entries.[/yellow]")
    else:
        if not typer.confirm(f"Remove {len(missing_files)} missing files from index?"):
            conn.close()
            return

        # Remove missing files
        for file_id, file_path in missing_files:
            conn.execute("DELETE FROM files WHERE id = ?", (file_id,))

        conn.commit()
        console.print(f"✅ Removed {len(missing_files)} missing files from index.")

        # Update aggregates
        console.print("🔄 Updating aggregates...")
        indexer.update_aggregates()

        console.print("✅ Index cleanup complete!")

    conn.close()

@app.command("export")
def export_index(output: str, db_path: str = None, format: str = typer.Option("json", help="Output format (json, csv)")):
    """
    Export the library index to a file.

    Args:
        output: Output file path
        db_path: Custom database path (optional)
        format: Output format (json or csv)
    """
    indexer = get_indexer(db_path)

    if not indexer.db_path.exists():
        console.print("❌ No index found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    output_file = Path(output)
    conn = sqlite3.connect(indexer.db_path)

    # Get all file data with tags
    data = conn.execute("""
        SELECT f.path, f.filename, f.directory, f.size, f.hash, f.modified, f.indexed,
               f.length, f.bitrate, f.sample_rate, f.channels, f.bits_per_sample,
               t.title, t.artist, t.album, t.albumartist, t.date, t.genre, t.track, t.disc,
               t.composer, t.performer, t.label, t.isrc, t.barcode, t.catalog, t.comment, t.copyright
        FROM files f
        LEFT JOIN tags t ON f.id = t.file_id
        ORDER BY t.artist, t.album, t.track
    """).fetchall()

    conn.close()

    if format.lower() == "json":
        # Convert to JSON format
        json_data = []
        for row in data:
            json_data.append({
                "path": row[0],
                "filename": row[1],
                "directory": row[2],
                "size": row[3],
                "hash": row[4],
                "modified": row[5],
                "indexed": row[6],
                "length": row[7],
                "bitrate": row[8],
                "sample_rate": row[9],
                "channels": row[10],
                "bits_per_sample": row[11],
                "title": row[12],
                "artist": row[13],
                "album": row[14],
                "albumartist": row[15],
                "date": row[16],
                "genre": row[17],
                "track": row[18],
                "disc": row[19],
                "composer": row[20],
                "performer": row[21],
                "label": row[22],
                "isrc": row[23],
                "barcode": row[24],
                "catalog": row[25],
                "comment": row[26],
                "copyright": row[27]
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        console.print(f"✅ Exported {len(data)} records to JSON: {output_file}")

    elif format.lower() == "csv":
        import csv

        headers = [
            "path", "filename", "directory", "size", "hash", "modified", "indexed",
            "length", "bitrate", "sample_rate", "channels", "bits_per_sample",
            "title", "artist", "album", "albumartist", "date", "genre", "track", "disc",
            "composer", "performer", "label", "isrc", "barcode", "catalog", "comment", "copyright"
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)

        console.print(f"✅ Exported {len(data)} records to CSV: {output_file}")

    else:
        console.print(f"❌ Unsupported format: {format}", style="red")
        raise typer.Exit(1)

@app.command("info")
def index_info(db_path: str = None):
    """
    Show information about the index database.

    Args:
        db_path: Custom database path (optional)
    """
    indexer = get_indexer(db_path)

    if not indexer.db_path.exists():
        console.print("❌ No index found. Run 'fla lib index build' first.", style="red")
        raise typer.Exit(1)

    # Get database info
    db_size = indexer.db_path.stat().st_size
    db_modified = datetime.fromtimestamp(indexer.db_path.stat().st_mtime)

    # Display info
    table = Table(title="Index Database Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Database Path", str(indexer.db_path))
    table.add_row("Database Size", f"{db_size:,} bytes")
    table.add_row("Last Modified", db_modified.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)

    # Show table statistics
    conn = sqlite3.connect(indexer.db_path)

    tables = ["files", "tags", "custom_tags", "albums", "artists"]

    for table_name in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        table.add_row(f"{table_name.title()} Records", str(count))

    conn.close()

    console.print(table)
