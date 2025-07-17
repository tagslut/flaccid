# FLACCID Architecture Documentation

This directory contains architectural documentation for the FLACCID CLI toolkit, including system design, architectural decisions, and technical specifications.

## Overview

FLACCID follows a modular plugin-based architecture designed for extensibility and maintainability. The system is organized into distinct layers that separate concerns and enable independent development of components.

## Architecture Layers

### CLI Layer
- **Entry Point**: `src/flaccid/cli/__init__.py` - Main Typer application
- **Command Groups**: `src/flaccid/commands/` - Organized command implementations
- **User Interface**: Rich-based progress indicators and interactive elements

### Plugin System
- **Base Classes**: `src/flaccid/plugins/base.py` - Abstract interfaces and data models
- **Service Plugins**: Individual implementations for music services (Qobuz, Apple Music, Tidal)
- **Provider Types**: Metadata providers, download providers, lyrics providers

### Core Services
- **Configuration**: `src/flaccid/core/config.py` - Dynaconf + Pydantic settings management
- **Metadata**: `src/flaccid/core/metadata.py` - Tag writing and metadata cascade logic
- **Downloads**: `src/flaccid/core/downloader.py` - Async file download utilities
- **Library**: `src/flaccid/core/library.py` - File scanning and indexing
- **Database**: SQLAlchemy ORM with SQLite backend

## Key Architectural Principles

### Separation of Concerns
- **CLI commands** handle user interaction and argument parsing
- **Plugins** manage service-specific API integration
- **Core modules** provide shared functionality and business logic
- **Configuration** is centralized and validated

### Plugin Architecture
- **Abstract base classes** define consistent interfaces
- **Service-specific implementations** handle API differences
- **Metadata normalization** ensures consistent data structures
- **Error handling** provides graceful fallbacks

### Asynchronous Design
- **aiohttp** for non-blocking HTTP operations
- **asyncio** for concurrent downloads and API calls
- **Rich** for real-time progress display
- **Watchdog** for filesystem monitoring

### Data Flow

```
User Input (CLI) → Command Handler → Plugin → API Service
                                  ↓
Core Services ← Normalized Data ← Plugin Response
     ↓
File System / Database
```

## Plugin System Design

### Plugin Types

#### MetadataProviderPlugin
- Fetches track and album metadata from external services
- Implements search, lookup, and metadata retrieval methods
- Examples: Apple Music (iTunes API), Qobuz, Tidal

#### DownloadProviderPlugin  
- Handles track downloads from streaming services
- Manages authentication and download URLs
- Examples: Qobuz, Tidal (planned)

#### LyricsProviderPlugin
- Retrieves lyrics from external sources
- Integrates with metadata tagging workflow
- Examples: lyrics.ovh, Genius API (planned)

### Plugin Interface

All plugins inherit from `BasePlugin` and implement:
- `async def open()` - Initialize resources
- `async def close()` - Clean up resources
- Service-specific methods for their functionality

### Metadata Cascade

The metadata cascade system merges information from multiple sources:
1. **Primary source** provides base metadata
2. **Fallback sources** fill missing fields
3. **Conflict resolution** handles overlapping data
4. **Validation** ensures data quality

## Configuration Architecture

### Settings Hierarchy
1. **Environment variables** (highest priority)
2. **Configuration files** (.secrets.toml, settings.toml)
3. **Default values** (lowest priority)

### Credential Management
- **Keyring integration** for secure storage
- **Service-specific tokens** managed separately
- **Environment variable fallbacks** for CI/CD

### Validation
- **Pydantic models** ensure type safety
- **Configuration schema** validates required fields
- **Runtime validation** catches configuration errors

## Database Schema

### Core Tables
- **tracks** - Individual track metadata and file paths
- **albums** - Album-level information and relationships
- **sources** - Track metadata source attribution

### Indexing Strategy
- **Full-text search** on track and album titles
- **File path indexing** for efficient lookups
- **Metadata indexing** for filtering and sorting

## Security Considerations

### Credential Storage
- **System keyring** integration (Keychain, Credential Manager)
- **No plaintext passwords** in configuration or code
- **Token refresh** mechanisms for expired credentials

### API Security
- **Rate limiting** to respect service limits
- **Error handling** to prevent credential leakage
- **HTTPS enforcement** for all external communications

## Performance Considerations

### Async Operations
- **Concurrent downloads** for album processing
- **Non-blocking I/O** for file operations
- **Progress tracking** for user feedback

### Caching Strategy
- **Metadata caching** to reduce API calls
- **File integrity checks** to avoid re-downloads
- **Database indexing** for fast queries

### Memory Management
- **Streaming downloads** to handle large files
- **Lazy loading** of plugin modules
- **Resource cleanup** in async contexts

## Architecture Decision Records (ADRs)

The `adr/` directory contains formal architectural decisions:

- **[ADR-002: Adopt GPL License](../../docs/architecture/adr/002-adopt-gpl-license.md)** - License selection rationale

## Extension Points

### Adding New Services
1. Create plugin class inheriting from appropriate base
2. Implement required interface methods
3. Add configuration schema entries
4. Register plugin in command handlers

### Custom Metadata Sources
1. Implement `MetadataProviderPlugin` interface
2. Add service-specific configuration
3. Integrate with metadata cascade system
4. Add CLI command integration

### Database Extensions
1. Define new SQLAlchemy models
2. Create migration scripts
3. Update indexing strategies
4. Modify query interfaces

## Testing Architecture

### Test Organization
- **Unit tests** for individual components
- **Integration tests** for plugin interactions
- **CLI tests** for command-line interface
- **End-to-end tests** for complete workflows

### Mock Strategy
- **API response mocking** for external services
- **File system mocking** for library operations
- **Database mocking** for data layer tests

## Deployment Considerations

### Packaging
- **Poetry** for dependency management
- **pyproject.toml** for project configuration
- **Console scripts** for CLI entry points

### Distribution
- **PyPI packaging** for public distribution
- **Docker containers** for isolated deployment
- **GitHub Actions** for automated releases

## Future Architecture Enhancements

### Planned Improvements
- **Plugin discovery** system for third-party extensions
- **Distributed processing** for large library operations
- **Web interface** for remote management
- **API server** mode for programmatic access

### Scalability Considerations
- **Database sharding** for very large libraries
- **Microservice architecture** for cloud deployment
- **Event-driven processing** for real-time updates

---

*For detailed implementation information, see the [Developer Handbook](../../docs/FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md).*