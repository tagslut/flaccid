# FLACCID CLI Toolkit Documentation

Welcome to the FLACCID CLI Toolkit documentation. This directory contains comprehensive documentation for developers and users.

Return to the [project README](../README.md) for installation instructions and an overview.

## Overview

FLACCID (FLAC Library and Canonical Content Identification) is a modular command-line toolkit designed for managing FLAC audio libraries and integrating with music streaming services. It enables users to download high-quality music from Qobuz, tag their local FLAC files with rich metadata (including album art and lyrics), and maintain a well-organized music library database.

## Documentation Structure

### User Documentation
- **[User Guide](user-guide.md)** - Complete usage guide with examples and best practices
- **[Installation Guide](installation.md)** - Step-by-step installation instructions
- **[Configuration Guide](configuration.md)** - How to configure credentials and settings
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### Developer Documentation
- **[Developer Handbook](FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md)** - Comprehensive technical documentation (4044 lines)
- **[Architecture Overview](architecture/README.md)** - System architecture, design patterns, and technical specifications
- **[Architecture Decision Records](architecture/adr/)** - Formal architectural decisions and rationale
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project

### Project Status
- **[Project Status](PROJECT_STATUS.md)** - Current implementation status and roadmap
- **[Phase 2 Plan](PHASE2_PLAN.md)** - Detailed implementation plan for Phase 2
- **[Development Log](development-log.md)** - Historical development notes and decisions
- **[Changelog](../CHANGELOG.md)** - Version history and changes

### Reference
- **[API Reference](api-reference.md)** - Complete API documentation
- **[CLI Reference](cli-reference.md)** - All CLI commands and options
- **[Configuration Reference](config-reference.md)** - All configuration options

## Quick Start

### Installation
```bash
git clone https://github.com/your-repo/flaccid.git
cd flaccid
chmod +x setup.sh
./setup.sh
```

### Basic Usage
```bash
# Store credentials
fla settings store qobuz --token YOUR_TOKEN

# Download a track
fla download qobuz 12345678 song.flac

# Tag a file with Apple Music metadata
fla meta apple song.flac --track-id 12345678

# Scan your library
fla library scan ~/Music --db library.db
```

## Key Features

- **Track Downloads**: Download tracks from Qobuz with quality selection
- **Metadata Tagging**: Apply rich metadata from Apple Music and other sources
- **Library Management**: Scan and index your music collection with SQLite
- **Credential Storage**: Secure credential management via system keyring
- **Duplicate Detection**: Find and manage duplicate files
- **Metadata Cascade**: Merge metadata from multiple providers
- **Asynchronous Operations**: Efficient parallel downloads and processing

## Architecture

FLACCID follows a modular plugin-based architecture:

- **CLI Layer**: Typer-based command interface (`fla` command)
- **Plugin System**: Extensible plugins for different music services
- **Core Modules**: Shared functionality for metadata, downloading, and library management
- **Configuration**: Dynaconf-based settings with Pydantic validation
- **Database**: SQLAlchemy ORM with SQLite backend

## Supported Services

### Fully Implemented
- **Qobuz**: Authentication, metadata, downloads
- **Apple Music**: Metadata via iTunes Search API

### In Development
- **Tidal**: Basic structure, authentication pending
- **Lyrics Providers**: Integration with lyrics.ovh and other services

### Planned
- **Discogs**: Metadata provider
- **MusicBrainz**: Metadata provider
- **Beatport**: Electronic music specialist

## Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md) for common issues
- Review the [User Guide](user-guide.md) for detailed usage instructions
- See the [Developer Handbook](FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md) for technical details
- Open an issue on GitHub for bugs or feature requests

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Development setup

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](../LICENSE) file for details.

---

*Last updated: Wed Jul 16 18:07:05 EEST 2025*
