# CHANGELOG.md

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-07-16
### Core Architecture and Plugin Loading
- Rewrote `PluginLoader` to support proper package-relative imports using `SourceFileLoader`. This resolves failures caused by relative imports (`from .base import ...`) when loading plugins from source files.
- Improved plugin registry to skip internal modules and support fallback discovery through the `FLACCID_PLUGIN_PATH` environment variable.

### Metadata Cascade Engine
- Extended `cascade()` logic to accept user-defined plugin precedence, allowing flexible control over metadata sourcing.
- Added per-field merge strategy support: `prefer`, `replace`, and `append`. These strategies can now be specified in the config or CLI.
- Implemented a validation mechanism to ensure no metadata fields are lost when combining results from multiple providers.

### Lyrics System Enhancements
- Integrated LRC (synchronized lyrics) export with `--export-lrc` CLI flag. When available, synced lyrics are saved in `.lrc` format beside the audio file.
- Implemented a per-track LRU cache for lyrics to prevent repeated API calls for commonly queried tracks.
- Improved fallback logic for lyrics providers. Now attempts Genius → Musixmatch → Lyrics.ovh, logging the failure reason for each provider.

### Library Management & Search
- Implemented full-text search across indexed title, artist, album fields using SQLite FTS5.
- Added advanced CLI options for `fla library search`: `--filter`, `--sort`, `--limit`, and `--offset` to improve large collection browsing.
- Added `fla library missing` command to identify tracks with incomplete metadata (missing title, artist, or album).

### Testing and Reliability
- Reached ≥85% test coverage for all major plugin and core modules. Pytest now fails if coverage falls below threshold.
- Added integration tests covering complete CLI workflows: search → download → cascade → tag → validate output.
- All external API calls to Tidal and lyrics providers are now mocked for unit and integration testing. This ensures reliability and reproducibility in CI environments.

### Documentation and Developer Experience
- Finalized and published the following documentation files:
  - `CODE_OF_CONDUCT.md`
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `docs/plugin-development.md` (new)
- Expanded `docs/user-guide.md` to include real-world CLI examples, plugin discovery setup, and cascade strategy configuration.
- Updated `README.md` to reflect new commands and environment variables.

---

## [0.1.0] - 2025-07-10
- Project structure finalized with Poetry and src/ layout.
- All legacy code archived; only modern modules in use.
- Pre-commit hooks and mypy fully integrated and passing.
- Documentation and developer onboarding improved.

## [0.0.4] - 2025-07-09
- Unified Canonical Payload (UCP) schema for metadata finalized.
- Qobuz, Apple Music, and MusicBrainz API integration verified.
- Picard-style filename template logic implemented.
- Discogs and AcoustID API keys confirmed and integrated.

## [0.0.3] - 2025-07-08
- Merge conflicts resolved in core modules.
- CI workflow updated for coverage reporting.
- Dependency issues fixed and poetry.lock regenerated.

## [0.0.2] - 2025-07-07
- Beatport API integration and session summary added.
- CI pipeline triggers verified and fixed.
- Type safety improved in config.py.

## [0.0.1] - 2025-07-06
- Initial implementation of Qobuz and Apple Music APIs.
- SQLite database integration for library indexing.
- Modular CLI structure using Typer established.

## [Unreleased]
- ...
