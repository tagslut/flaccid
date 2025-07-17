# FLACCID CLI User Guide

This comprehensive guide covers all aspects of using the FLACCID CLI toolkit for managing your FLAC music library.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Core Commands](#core-commands)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Store Credentials

Save your service credentials in the system keyring:

```bash
fla settings store qobuz --token YOUR_QOBUZ_TOKEN
fla settings store apple --token YOUR_APPLE_TOKEN
```

### 2. Download Music

Download tracks from supported services:

```bash
fla download qobuz 12345678 song.flac
```

### 3. Tag Files

Apply Apple Music metadata to a track:

```bash
fla meta apple /path/to/song.flac --track-id 123456789
  --strategy.title replace
```

### 4. Manage Your Library

```bash
fla library scan /path/to/music --db library.db
fla library watch start /path/to/music --db library.db
# later
fla library watch stop /path/to/music
```

## Installation

### Automatic Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/flaccid.git
   cd flaccid
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The setup script automatically detects whether to use Poetry or pip and installs all dependencies.

### Manual Installation with Poetry

```bash
poetry install --sync
```

### Manual Installation with pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in your project root and set values such as:

```bash
QOBUZ_APP_ID=your_app_id
QOBUZ_TOKEN=your_token
APPLE_TOKEN=your_apple_token
```

The CLI loads these automatically when present.

### Credential Storage

Use the `settings store` command to securely store credentials:

```bash
fla settings store qobuz --token YOUR_QOBUZ_TOKEN
fla settings store apple --token YOUR_APPLE_TOKEN
```

Credentials are stored securely in your system keyring (Keychain on macOS, Credential Manager on Windows, etc.).

## Core Commands

### Download Commands (`fla download`)

Download music from supported streaming services.

#### Qobuz Downloads

```bash
# Download a single track
fla download qobuz 12345678 song.flac

# Download with specific quality
fla download qobuz 12345678 song.flac --quality hi-res
```

#### Tidal Downloads (Planned)

```bash
# Future feature
fla download tidal 12345678 song.flac
```

### Metadata Commands (`fla meta`)

Apply metadata to local FLAC files from various sources.

#### Apple Music Tagging

```bash
# Tag a file with Apple Music metadata
fla meta apple /path/to/song.flac --track-id 123456789

# Tag with custom filename template
fla meta apple /path/to/song.flac --track-id 123456789 \
  --template "{artist} - {title}.flac"
  --strategy.title replace
```

#### Authentication and Status

```bash
# Check authentication status (placeholder)
fla meta apple --status

# Authenticate (placeholder for future implementation)
fla meta apple --auth
```

### Library Management (`fla library`)

Manage your local music library database.

#### Scanning

```bash
# Scan a directory and index files
fla library scan /path/to/music --db library.db

# Scan with continuous watching
fla library scan /path/to/music --db library.db --watch
```

#### Watching

```bash
# Start watching a directory
fla library watch start /path/to/music --db library.db

# Stop watching a directory
fla library watch stop /path/to/music
```

#### Searching

```bash
# Search your library for "beatles" sorted by title
fla library search --filter "beatles" --sort title --limit 20
```

### Settings Commands (`fla settings`)

Manage credentials and configuration.

```bash
# Store a service token
fla settings store qobuz --token YOUR_TOKEN

# Store credentials for different services
fla settings store apple --token YOUR_APPLE_TOKEN
fla settings store tidal --token YOUR_TIDAL_TOKEN
```

## Advanced Usage

### Metadata Cascade

FLACCID supports merging metadata from multiple sources to fill in missing fields. The `cascade` helper in the core metadata module combines metadata objects left-to-right, filling gaps automatically.

### Filename Templates

When tagging files, you can specify custom filename templates:

```bash
fla meta apple song.flac --track-id 123456789 \
  --template "{track_number:02d} - {artist} - {title}.flac"
  --strategy.lyrics append
```

Available template variables:
- `{artist}` - Track artist
- `{title}` - Track title
- `{album}` - Album name
- `{track_number}` - Track number
- `{disc_number}` - Disc number

### Lyrics Cache and LRC Export

Lyrics fetched during tagging are stored in `~/.cache/flaccid/lyrics`. The cache
is keyed by track ID (if available) or the file hash. Use the ``--export-lrc``
flag with ``fla tag apply`` to write a synchronized ``.lrc`` file next to your
FLAC track:

```bash
fla tag apply song.flac --metadata-file meta.json --export-lrc
```

### Duplicate Detection

Find and manage duplicate FLAC files in your library:

```bash
# Find duplicates by file hash (most accurate)
fla duplicates find ~/Music --by hash

# Find duplicates by title
fla duplicates find ~/Music --by title

# Find duplicates by filename
fla duplicates find ~/Music --by filename --recursive

# Find duplicates by artist and title combination
fla duplicates find ~/Music --by artist+title

# Only consider files larger than 5MB
fla duplicates find ~/Music --min-size 5000

# Export results to JSON file
fla duplicates find ~/Music --export duplicates.json

# Remove duplicates interactively
fla duplicates remove ~/Music --by hash --strategy interactive --no-dry-run

# Automatically keep the highest quality version
fla duplicates remove ~/Music --by hash --strategy keep-highest-quality --no-dry-run

# Keep the newest file of each duplicate set
fla duplicates remove ~/Music --by hash --strategy keep-newest --no-dry-run
```

### Development Mode

During development, run commands with `poetry run`:

```bash
poetry run python -m fla download qobuz 12345678 song.flac
poetry run python -m fla meta apple song.flac --track-id 12345678
  --strategy.title replace
poetry run python -m fla library scan ~/Music --db library.db
```

## Best Practices

### File Management

1. **Always back up your FLAC files** before modifying tags
2. **Use consistent directory structures** for your music library
3. **Test commands on a small subset** before processing large libraries

### Security

1. **Use environment variables** for API keys when possible
2. **Store credentials securely** using the `settings store` command
3. **Never commit API keys** to version control

### Performance

1. **Avoid heavy batch operations** that exceed API rate limits
2. **Use the watch functionality** for real-time library updates
3. **Consider file sizes** when processing large libraries

### Quality

1. **Verify metadata accuracy** after tagging operations
2. **Use multiple metadata sources** to fill in missing information
3. **Check file integrity** after downloads

## Troubleshooting

### Common Issues

#### Authentication Failures
- **Problem**: Commands fail with authentication errors
- **Solution**: Verify stored tokens with your keyring tool
- **Check**: Run `fla meta apple --status` to verify authentication

#### File Access Errors
- **Problem**: Permission denied when accessing files
- **Solution**: Ensure the process has read/write permissions to the target directory
- **Check**: Verify file ownership and permissions

#### API Rate Limits
- **Problem**: Commands fail due to too many requests
- **Solution**: Avoid heavy batch operations, add delays between requests
- **Check**: Review API documentation for rate limit information

#### Missing Dependencies
- **Problem**: Import errors or missing modules
- **Solution**: Reinstall dependencies using the setup script
- **Check**: Run `poetry install --sync` or `pip install -r requirements.txt`

### Getting Help

1. **Use `--help`** with any command for detailed usage information:
   ```bash
   fla --help
   fla download --help
   fla meta apple --help
   ```

2. **Check the logs** for detailed error information

3. **Review the configuration** to ensure all required settings are present

4. **Consult the Developer Handbook** for technical details

### Error Messages

#### "Track with ID 'X' not found"
- The specified track ID doesn't exist in the service's database
- Verify the track ID is correct and the track is available in your region

#### "Path not found"
- The specified file or directory doesn't exist
- Check the path spelling and ensure the file exists

#### "Failed to authenticate"
- Invalid or expired credentials
- Re-run the authentication setup: `fla settings store [service]`

## CLI Structure Summary

- **`download`** – Download music from Qobuz (Tidal and Beatport planned)
- **`meta`** – Apply metadata from Apple Music and other sources
- **`library`** – Scan folders and build SQLite index with watch capabilities
- **`settings`** – Store credentials securely in the system keyring
- **`duplicates`** – Find and manage duplicate files

Each command group provides focused functionality while maintaining a consistent interface and help system.

---

*For more detailed technical information, see the [Developer Handbook](FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md).*