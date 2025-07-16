# FLACCID CLI Toolkit - Project Status and Roadmap

## ✅ Completed Features

### Core CLI Framework
- CLI entrypoint (`flaccid/cli.py`) built on **Typer**
- Command groups: `download`, `meta`, `library`, `settings`
- Typer-based command groups with basic subcommands:
  - `meta fetch`, `meta apply`
  - `download qobuz`, `download tidal` (stub)
  - `library scan`, `library watch`
  - `settings store`
- Legacy `fla` shim for backward compatibility

### Plugin Framework
- **Abstract plugin interfaces** defining track/album metadata and service behavior
- **Plugin registry** includes working Qobuz implementation and placeholder modules for Apple, Beatport, Discogs, Lyrics, and Tidal
- **Dataclasses and base classes** for consistent plugin development
- Only `QobuzPlugin` currently supports full authentication, search, and downloads

### Qobuz Plugin
- **Full authentication** via Qobuz API with token management
- **Album and track metadata fetching** with comprehensive field mapping
- **Async track downloading** with quality selection and progress tracking
- **FLAC file tagging** via `fla meta qobuz` command
- **Error handling** for API failures and rate limiting

### Apple Music Plugin
- **Metadata provider** via iTunes Search API (no authentication required)
- **Album search** by query or ID with comprehensive metadata
- **Track lookup** by ID or ISRC code
- **Tagging support** via `fla meta apple` command

### Tagging System
- **Implemented with Mutagen** for FLAC file manipulation:
  - Embedding track/album metadata (title, artist, album, etc.)
  - Cover art embedding with automatic format detection
  - Lyrics integration with external providers
- **Metadata cascade functionality** for merging multiple sources
- **Filename template support** for organized file naming
- **Tag fetch and apply commands** for flexible workflow

### Library Management
- **Directory scanning** with recursive FLAC file detection
- **SQLite database integration** via SQLAlchemy ORM
- **File indexing** with metadata extraction and storage
- **Watch functionality** using Watchdog for real-time updates
- **Library scan command** with optional continuous monitoring
- **Index management** with verification capabilities

### Configuration Management
- **Dynaconf-based settings** with TOML and environment variable support
- **Secure credential storage** via system Keyring
- **Pydantic validation** for configuration schema
- **CLI configuration commands**:
  - `settings store` for credential management
  - Environment variable integration

### Code Structure and Quality
- **Modular organization** under `src/flaccid/`:
  - `cli/`, `commands/`, `core/`, `plugins/`
- **Comprehensive test suite** with pytest framework
- **GitHub Actions CI/CD** with pre-commit hooks
- **Type safety** with mypy integration
- **Code formatting** with black, isort, autoflake
- **Dependency management** via Poetry

---

## ❌ Incomplete / Pending Features

### Tidal Plugin
- Basic stub exists.
- OAuth flow and metadata retrieval **not yet functional**.
- Download capabilities **absent**.

### Lyrics Plugin
- Abstract base defined.
- No working implementation (e.g., **Genius API** integration pending).

### File Watcher for Library Updates
- Watchdog-based real-time monitoring **not implemented**.

### Index Verification Enhancements
- `fla lib index` exists but:
  - No deep integrity checks (e.g., checksums).
  - No duplicate detection mechanisms.

### Plugin System Formalization
- Abstract plugin base classes defined.
- No dynamic loader or registration mechanism for 3rd-party plugins.

### Documentation
- Developer handbook and scaffold guide available.
- No formal **user-facing documentation** or **installation guides**.

### Additional Metadata Sources
- Discogs: **Not implemented**.
- MusicBrainz: **Not implemented**.
- Beatport: **Not implemented**.

### Testing
- Tests scaffolded but:
  - No full coverage.
  - No CI testing pipeline yet.

### Error Handling
- Core flows exist.
- No robust error handling, retries, or graceful fallbacks for network or API failures.

---

## 🔜 Next Priorities (Roadmap)

### Short-term
1. **Complete Tidal Plugin**
   - OAuth Device Code Flow.
   - Metadata fetching.
   - Download support.

2. **Implement Lyrics Plugin**
   - Integrate with Genius API.
   - Optional fallback to Musixmatch.

3. **Develop Plugin Loader System**
   - Dynamic plugin discovery.
   - Plugin registration API.

4. **Enhance `lib index`**
   - Add checksum verification.
   - Implement duplicate detection.

5. **Formalize Error Handling**
   - Retry logic for downloads.
   - Graceful fallbacks for API timeouts.

### Medium-term
6. **Implement Metadata Plugins**
   - Discogs.
   - MusicBrainz.
   - Beatport.

7. **Develop File Watcher for Library**
   - Watchdog-based auto-indexing.

8. **Expand Test Coverage**
   - Implement unit, integration, and regression tests.
   - Establish CI pipeline.

9. **Write User Documentation**
   - Usage guide.
   - Installation instructions.
   - Troubleshooting.

### Long-term
10. **Community Plugin Support**
    - Provide SDK/documentation for external plugin developers.

11. **Performance Optimizations**
    - Async processing improvements.
    - Caching for metadata queries.

---

## 📌 Recommendations
- Prioritize the Tidal and Lyrics plugins to complete the core functional scope.
- Establish CI to prevent regressions.
- Expand documentation for adoption beyond developer users.

---

Prepared for: **Georges Khawam**
Date: **2025-07-16**

