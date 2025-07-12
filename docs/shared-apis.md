# FLACCID - Shared APIs

This document describes the shared API modules for the FLACCID CLI toolkit.

## Overview

The shared API modules provide reusable, async-first interfaces for music metadata services:

- **`shared/qobuz_api.py`** - Qobuz API client with authentication and metadata retrieval
- **`shared/apple_api.py`** - Apple Music API client with iTunes fallback
- **`shared/metadata_utils.py`** - Common FLAC metadata operations
- **`shared/config.py`** - Configuration management with .env support

## Configuration

### Environment Variables

Create a `.env` file in your project root (use `.env.template` as a starting point):

```bash
# Qobuz Configuration
QOBUZ_APP_ID=your_qobuz_app_id_here
QOBUZ_TOKEN=your_qobuz_auth_token_here

# Apple Music Configuration
APPLE_TOKEN=your_apple_music_developer_token_here
APPLE_STORE=us

# Tidal Configuration
TIDAL_TOKEN=your_tidal_auth_token_here
TIDAL_USERNAME=your_tidal_username
TIDAL_PASSWORD=your_tidal_password

# General Configuration
FLACCID_LOG_LEVEL=INFO
FLACCID_CACHE_DIR=~/.flaccid/cache
```

### Keyring Storage

For secure credential storage, use the auth commands:

```bash
# Store Qobuz credentials
fla set auth qobuz --username your_username --password your_password

# Store Apple Music tokens
fla set auth apple --developer-token your_token --user-token optional_user_token
```

## API Usage

### Qobuz API

```python
from flaccid.shared.qobuz_api import QobuzAPI

async def example():
    async with QobuzAPI() as qobuz:
        # Search for tracks
        results = await qobuz.search("artist track name")

        # Get track metadata
        metadata = await qobuz.get_track_metadata("12345")

        # Get album metadata
        album = await qobuz.get_album_metadata("67890")
```

### Apple Music API

```python
from flaccid.shared.apple_api import AppleAPI

async def example():
    async with AppleAPI() as apple:
        # Search tracks (uses iTunes API as fallback)
        results = await apple.search("artist track name")

        # Lookup by ISRC
        track = await apple.lookup_by_isrc("USRC17607839")

        # Get track details (requires Apple Music API token)
        track = await apple.get_track("12345")
```

### Metadata Utils

```python
from flaccid.shared.metadata_utils import (
    validate_flac_file,
    get_existing_metadata,
    build_search_query,
    extract_isrc_from_flac
)

# Validate FLAC file
if validate_flac_file("/path/to/file.flac"):
    # Get existing metadata
    metadata = get_existing_metadata("/path/to/file.flac")

    # Build search query
    query = build_search_query(metadata)

    # Extract ISRC if available
    isrc = extract_isrc_from_flac("/path/to/file.flac")
```

## Features

### Qobuz API Features
- ✅ Token-based authentication with keyring support
- ✅ Track search and metadata retrieval
- ✅ Album metadata retrieval
- ✅ Streaming URL generation (subscription required)
- ✅ Automatic token refresh
- ✅ Async context manager support

### Apple Music API Features
- ✅ Developer token authentication
- ✅ iTunes Search API fallback (no auth required)
- ✅ ISRC-based lookups
- ✅ Track and album metadata retrieval
- ✅ User token support for personalized features
- ✅ Async context manager support

### Tidal API Features
- ✅ Token or credential based authentication
- ✅ Track search and metadata retrieval
- ✅ Album metadata retrieval
- ✅ Streaming URL generation
- ✅ Async context manager support

### Metadata Utils Features
- ✅ FLAC file validation
- ✅ Metadata extraction from existing files
- ✅ Search query building from metadata
- ✅ ISRC extraction from FLAC tags
- ✅ Generic metadata application

## Error Handling

All APIs include comprehensive error handling:

- Network errors are caught and logged
- Authentication failures trigger re-authentication
- Rate limiting is respected
- Graceful degradation (e.g., iTunes fallback for Apple Music)

## Testing

Run the unit tests:

```bash
poetry run pytest tests/test_shared_apis.py -v
```

Tests cover:
- Configuration management
- API initialization
- Async context managers
- Mocked API responses
- Metadata utility functions

## Dependencies

Required packages:
- `aiohttp` - Async HTTP client
- `keyring` - Secure credential storage
- `mutagen` - FLAC metadata handling
- `python-dotenv` - Environment variable loading
- `rich` - Console output formatting

## Next Steps

1. **Fallback Enrichment**: Add MusicBrainz and Discogs APIs
2. **Caching**: Implement response caching for better performance
3. **Rate Limiting**: Add proper rate limiting for API calls
4. **Batch Operations**: Optimize for bulk metadata operations
5. **Additional Services**: Add Tidal, Spotify, etc.
