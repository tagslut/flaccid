# Copilot Instructions for FLACCID CLI Toolkit

## Overview
FLACCID is a CLI toolkit for managing and enriching FLAC music libraries. It integrates with APIs like Qobuz, Apple Music, and others to provide metadata enrichment, tagging, and library management features. The project is modular, with a plugin system for extending functionality.

## Architecture
- **Core Components**:
  - `src/flaccid/cli.py`: Entry point for CLI commands.
  - `src/flaccid/core/`: Core logic for library management and metadata handling.
  - `src/flaccid/plugins/`: Modular plugins for API integrations.
  - `src/flaccid/shared/`: Shared utilities and helper functions.
- **Data Flow**:
  - CLI commands invoke core logic.
  - Core logic interacts with plugins for API calls.
  - Results are processed and applied to FLAC files or stored in SQLite databases.

## Developer Workflows
### Build and Install
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/flaccid.git
   cd flaccid
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

### Testing
Run tests using pytest:
```bash
pytest
```

### Debugging
Use verbose mode for CLI commands:
```bash
fla tag fetch <file> --provider qobuz --verbose
```

## Project-Specific Conventions
- **CLI Commands**:
  - Use `fla` as the main command.
  - Subcommands include `tag`, `lib`, `set`, and `get`.
- **Plugin System**:
  - Plugins are located in `src/flaccid/plugins/`.
  - Each plugin must implement a standard interface defined in `src/flaccid/shared/`.
- **Testing**:
  - Unit tests are in `tests/unit/`.
  - Use fixtures for mocking API responses.

## Integration Points
- **External APIs**:
  - Qobuz, Apple Music, Discogs, Beatport.
- **Database**:
  - SQLite for library indexing.

## Examples
### Tagging Workflow
```bash
fla tag fetch <file> --provider qobuz
fla tag apply <file> --metadata-file tags.json --yes
```

### Library Management
```bash
fla lib scan /path/to/music --recursive
```
