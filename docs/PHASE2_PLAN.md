# FLACCID Phase 2 Implementation Plan

## Phase 2A: Core Expansion & Robustness

### 1. Plugin Expansion & Service Integration
- [ ] Qobuz Plugin: Complete async download, metadata, and error handling.
- [ ] Tidal Plugin: Implement full authentication, album/track metadata, and download logic.
- [ ] Apple Music Plugin: Expand ISRC and search-based tagging, improve fallback logic.
- [ ] Discogs/Beatport Plugins: Integrate for metadata enrichment and tagging.
- [ ] Lyrics Plugin: Add support for fetching and embedding lyrics from multiple sources.
- [ ] Plugin Interface: Refine abstract base classes for all plugin types.

### 2. Metadata Tagging & Cascade Logic
- [ ] Metadata Cascade: Implement logic to merge metadata from multiple sources with user-defined priority.
- [ ] Tagging Engine: Expand core/metadata.py to support album art, lyrics, and conditional/templated tag application.
- [ ] Filename Templates: Allow user-defined file/folder naming templates.
- [ ] Validation: Add pre-tagging validation (FLAC file integrity, tag conflicts).

### 3. Library Management & Indexing
- [ ] Database Schema: Expand SQLite schema for tracks, albums, artists, and analysis results.
- [ ] Incremental Indexing: Implement fast, incremental updates based on file changes.
- [ ] File Watcher: Integrate Watchdog for real-time library updates.
- [ ] Advanced Search: Add full-text and filtered search.
- [ ] Quality Analysis: Enhance reporting on sample rate, bit depth, and other audio properties.

### 4. Configuration & Security
- [ ] Dynaconf + Pydantic: Finalize config validation and environment layering.
- [ ] Keyring Integration: Ensure all credentials are stored/retrieved securely.
- [ ] Config Wizard: Add interactive setup for first-time users.
- [ ] .env & Secrets: Document and enforce best practices for sensitive data.


## Phase 2B: UX, Testing, Docs, and Release

### 5. CLI & User Experience
- [ ] Typer CLI: Ensure all command groups are fully implemented and documented.
- [ ] Help & Examples: Improve CLI help output with real-world examples.
- [ ] Error Handling: Add user-friendly error messages and recovery options.
- [ ] Progress Indicators: Use Rich for all long-running operations.

### 6. Testing & Quality
- [ ] Unit Tests: Expand tests for all plugins, core logic, and CLI commands.
- [ ] Integration Tests: Add end-to-end tests for real-world workflows.
- [ ] Mocking: Use mock APIs for testing external service integration.
- [ ] Coverage: Enforce coverage thresholds in CI.

### 7. Documentation & Developer Experience
- [ ] Update Developer Handbook: Reflect new modules, workflows, and best practices.
- [ ] API Docs: Generate and publish API documentation.
- [ ] Usage Guides: Expand usage examples and troubleshooting in docs/.
- [ ] Changelog & Roadmap: Keep CHANGELOG.md and TODO.md up to date.

### 8. Packaging & Deployment
- [ ] Poetry Packaging: Finalize pyproject.toml for all dependencies and entry points.
- [ ] Editable Installs: Support pip install -e . for development.
- [ ] Release Workflow: Automate versioning and publishing to PyPI.
- [ ] Docker Support: (Optional) Provide a Dockerfile for containerized usage.

---

Each phase can be tracked as a milestone, with tasks broken down into issues for assignment and progress tracking.
