# FLACCID Project Roadmap

This document outlines the key milestones and future priorities for the FLACCID CLI metadata and tagging toolkit. Development is guided by the principles of modularity, provider-neutral extensibility, and metadata integrity.

---

## ✅ Phase 1 – Core Architecture (COMPLETED)
- [x] Modular plugin system with shared base classes
- [x] Full Qobuz, Apple, and Tidal plugin support
- [x] Lyrics plugin with multi-source fallback (Genius, Musixmatch, Lyrics.ovh)
- [x] Incremental library indexing with multi-location support
- [x] Dynamic plugin loader using `FLACCID_PLUGIN_PATH`
- [x] Unified error handling system with base exception hierarchy
- [x] CLI interface using Typer
- [x] Metadata cascade engine with multi-source merging

---

## 🚧 Phase 2 – Developer Maturity

### Documentation
- [ ] Finalize `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`
- [ ] Maintain `CHANGELOG.md` with semantic versioning
- [ ] Expand user guide with full CLI and plugin usage examples
- [ ] Add plugin development documentation under `docs/`

### Testing & Quality
- [ ] Reach ≥85% test coverage across core and plugin modules
- [ ] Add integration tests for tag writing and download workflows
- [ ] Mock API responses for lyrics and Tidal endpoints

---

## 🔁 Phase 3 – Feature Expansion

### Metadata Cascade Engine
- [ ] Add configurable plugin precedence rules
- [ ] Support field-level merge strategies (append, prefer, replace)
- [ ] Validate field retention from all active sources

### Lyrics System
- [ ] Add synchronized lyrics (LRC) support with `.lrc` export
- [ ] Improve error handling and fallback awareness
- [ ] Add per-track lyrics cache

### Enhanced Search & Library Tools
- [ ] Full-text search across title, artist, and album fields
- [ ] Add CLI options: `--filter`, `--sort`, `--limit`, `--offset`
- [ ] Generate reports for missing metadata and duplicates

---

## 🚀 Phase 4 – Deployment & Distribution

### Release Automation
- [ ] Adopt full semantic versioning (`1.0.0`, `1.1.0`, etc.)
- [ ] GitHub Actions for testing, coverage, changelog, PyPI publishing
- [ ] Generate Docker images with CLI pre-installed

### Package Distribution
- [ ] Publish to PyPI (`pip install flaccid`)
- [ ] Create Homebrew formula or Shell installer
- [ ] Optional Flatpak or Snap builds (post-CLI GUI discussion)

---

## 🌍 Phase 5 – Community & Ecosystem

### Contributor Experience
- [ ] Label and maintain good-first issues
- [ ] Document PR review expectations and coding conventions
- [ ] Open call for new plugin contributions (Spotify, YouTube, Deezer)

### Ecosystem Integrations (Exploratory)
- [ ] Optional web interface or PWA dashboard
- [ ] macOS Automator/Shortcuts integration
- [ ] Mobile-friendly lyrics viewer/exporter
- [ ] Integration with music server APIs (Navidrome, Jellyfin)

---

## 🧪 Experimental Ideas (TBD)
- Acoustic ID-based auto-identification of local files
- Audio fingerprinting fallback with MusicBrainz
- Tag clustering suggestions for collections with inconsistent metadata
- FLAC-to-ALAC transcoding with retained metadata
- AI-powered metadata enrichment (artist origin, genre trends, liner notes)

---

**Feedback and contributions are welcome.**  
Please open issues, submit PRs, or join discussions via the GitHub tracker.
