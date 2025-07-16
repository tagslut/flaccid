# FLACCID CLI Toolkit - Project Status and Roadmap

## ✅ Completed Features

### Core CLI Framework
- CLI entrypoint (`flaccid/cli.py`) built on **Typer**.
- Commands:
  - `fla get`
  - `fla tag`
  - `fla lib`
  - `fla set`

### Qobuz Plugin
- Full authentication via Qobuz API.
- Album and track metadata fetching.
- Async track downloading with quality selection.
- FLAC file tagging via `fla tag qobuz`.

### Apple Music Plugin
- Metadata provider via iTunes Search API.
- Album search by query or ID.
- Tagging via `fla tag apple`.

### Tagging System
- Implemented with **Mutagen**:
  - Embedding track/album metadata.
  - Embedding cover art.
  - Placeholder for lyrics embedding.

### Library Management
- `fla lib scan`: Scans the library directory.
- `fla lib index`: Re-indexes with SQLAlchemy-based SQLite.

### Configuration Management
- Managed by **Dynaconf**.
- Secure credential storage via **Keyring**.
- CLI support for:
  - `fla set auth`
  - `fla set path`

### Code Structure
- Modular organization under `src/`:
  - `core/`, `plugins/`, `commands/`
- Test scaffolding in `tests/`.
- Dependency management via Poetry.

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

