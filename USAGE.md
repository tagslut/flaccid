# FLACCID Usage Examples

This document shows how to use the FLACCID CLI toolkit for tagging FLAC files.

## Quick Start

### 1. Setup Authentication

First, store your service credentials securely:

```bash
# Store Qobuz credentials
poetry run python -m fla set auth qobuz --username your_username --password your_password

# Store Apple Music developer token
poetry run python -m fla set auth apple --developer-token your_token

# List stored credentials
poetry run python -m fla set auth list
```

### 2. Setup Paths

Configure directory paths:

```bash
# Create default directories
poetry run python -m fla set path create

# Set custom music directory
poetry run python -m fla set path set music ~/Music/FLAC

# List configured paths
poetry run python -m fla set path list
```

### 3. Tag Files

#### Tag with Qobuz

```bash
# Tag by Qobuz track ID
poetry run python -m fla tag qobuz track /path/to/song.flac 12345678

# Interactive search and tag
poetry run python -m fla tag qobuz search /path/to/song.flac "Artist Song Title"

# Batch tag directory
poetry run python -m fla tag qobuz batch /path/to/music/directory --recursive
```

#### Tag with Apple Music

```bash
# Tag by ISRC (extracted from file if available)
poetry run python -m fla tag apple isrc /path/to/song.flac

# Tag with specific ISRC
poetry run python -m fla tag apple isrc /path/to/song.flac USRC17607839

# Interactive search and tag
poetry run python -m fla tag apple search /path/to/song.flac "Artist Song Title"

# Batch tag files with ISRC codes
poetry run python -m fla tag apple batch /path/to/music/directory --recursive

# Tag by Apple Music track ID
poetry run python -m fla tag apple track /path/to/song.flac 123456789
```

## Advanced Usage

### Environment Configuration

Create a `.env` file in your project root:

```bash
# Copy template and edit
cp .env.template .env

# Edit with your credentials
QOBUZ_APP_ID=your_qobuz_app_id
QOBUZ_TOKEN=your_qobuz_token
APPLE_TOKEN=your_apple_developer_token
APPLE_STORE=us
```

### Library Management (Placeholder)

```bash
# Scan directory for FLAC files
poetry run python -m fla lib scan directory /path/to/music

# Build library database
poetry run python -m fla lib index build

# Query library
poetry run python -m fla lib index query "search term"

# Show library stats
poetry run python -m fla lib index stats
```

### Download Music (Placeholder)

```bash
# Download from Qobuz
poetry run python -m fla get qobuz track 12345678
```

## CLI Structure

The FLACCID CLI is organized into modules:

- **`core`** - Core utilities and version info
- **`tag`** - Tag FLAC files with metadata
  - `qobuz` - Qobuz metadata tagging
  - `apple` - Apple Music metadata tagging
- **`set`** - Configuration and setup
  - `auth` - Manage authentication credentials
  - `path` - Configure directory paths
- **`lib`** - Library management
  - `scan` - Scan directories for FLAC files
  - `index` - Build and query music database
- **`get`** - Download music from services
  - `qobuz` - Download from Qobuz

## Metadata Tags Applied

### Qobuz Tags
- `TITLE` - Track title
- `ARTIST` - Track artist
- `ALBUM` - Album title
- `ALBUMARTIST` - Album artist
- `DATE` - Release date
- `GENRE` - Genre
- `LABEL` - Record label
- `TRACKNUMBER` - Track number
- `DISCNUMBER` - Disc number
- `COMPOSER` - Composer
- `FLACCID_QOBUZ_BITDEPTH` - Audio bit depth
- `FLACCID_QOBUZ_SAMPLERATE` - Sample rate

### Apple Music Tags
- `TITLE` - Track title
- `ARTIST` - Track artist
- `ALBUM` - Album title
- `ALBUMARTIST` - Album artist
- `DATE` - Release year
- `GENRE` - Primary genre
- `ISRC` - ISRC code
- `TRACKNUMBER` - Track number
- `TOTALTRACKS` - Total tracks on album
- `DISCNUMBER` - Disc number
- `TOTALDISCS` - Total discs
- `COPYRIGHT` - Copyright information
- `FLACCID_APPLE_TRACKID` - Apple Music track ID
- `FLACCID_APPLE_ALBUMID` - Apple Music album ID
- `FLACCID_APPLE_ARTISTID` - Apple Music artist ID
- `FLACCID_APPLE_COUNTRY` - Store country
- `FLACCID_APPLE_EXPLICIT` - Explicit content flag

## Error Handling

The CLI provides helpful error messages and handles common issues:

- **Invalid FLAC files**: Validates file format before processing
- **Missing credentials**: Prompts to set up authentication
- **API failures**: Graceful fallback and error reporting
- **Network issues**: Retry mechanisms and timeout handling
- **File permissions**: Clear error messages for access issues

## Testing

Run the unit tests to verify everything is working:

```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test module
poetry run pytest tests/test_simple.py -v

# Run with coverage
poetry run pytest tests/ --cov=flaccid --cov-report=html
```

## Tips

1. **ISRC Matching**: For best results with Apple Music, ensure your FLAC files have ISRC tags
2. **Batch Processing**: Use the `--recursive` flag to process entire directory trees
3. **Backup**: Always backup your FLAC files before batch tagging
4. **Credentials**: Use the keyring storage for security - avoid plain text credentials
5. **Environment**: Use `.env` files for easy configuration management

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running commands with `poetry run`
2. **Authentication Failures**: Check your stored credentials with `set auth list`
3. **File Access**: Ensure FLACCID has read/write access to your music files
4. **API Limits**: Respect service rate limits, especially for batch operations

### Getting Help

While the built-in help has formatting issues, you can:
- Check the source code in `src/flaccid/` for command details
- Refer to this documentation
- Run commands without arguments to see usage information
- Use the `core version` command to verify installation
