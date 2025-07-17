# FLACCID CLI Toolkit

[![CI](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Release](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/<your-org>/flaccid/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/flaccid?branch=main)

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [CLI Overview](#cli-overview)
- [Installation](#installation)
- [Plugin Loading](#plugin-loading)
- [Plugin Validation](#plugin-validation)
- [Usage](#usage)
  - [Library Scanning](#library-scanning)
  - [Metadata Tagging](#metadata-tagging)
  - [Database Indexing](#database-indexing)
  - [Finding and Managing Duplicates](#finding-and-managing-duplicates)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Running CI Locally](#running-ci-locally)
- [License](#license)

For a complete documentation index see [docs/README.md](docs/README.md).

## Overview

FLACCID is a simple CLI toolkit for downloading music and enriching FLAC files with metadata. It currently supports Apple Music tagging and downloading tracks from Qobuz. Library indexing utilities help keep a small SQLite database in sync with your collection.

## Key Features

- **Track Downloads**: `download qobuz` and `download tidal` save tracks locally.
- **Playlist Downloads**: `download tidal-playlist` fetches an entire playlist.
- **Metadata Tagging**: `meta apple` applies Apple Music metadata to FLAC files.
- **Library Management**: Scan and watch directories to keep an SQLite index up to date.
- **Credential Storage**: Store service tokens securely in your system keyring.
- **Duplicate Detection**: Find and manage duplicate FLAC files in your library.
- **Metadata Cascade**: Merge metadata from multiple providers to fill in any
  missing fields when tagging. The `cascade` helper lives in
  `src/flaccid/core/metadata.py`.

## CLI Overview

Run commands via the `fla` module:

```bash
poetry run python -m fla download qobuz 12345678 song.flac
poetry run python -m fla meta apple song.flac --track-id 12345678 \
  --template "{artist} - {title}.flac"
poetry run python -m fla library scan ~/Music --db library.db
poetry run python -m fla library watch start ~/Music ~/MoreMusic --db library.db
poetry run python -m fla settings store qobuz --token YOUR_TOKEN
```
Sample output for storing credentials:

```text
$ fla settings store qobuz --token YOUR_TOKEN
✅ Token stored for qobuz in system keyring
```

Each command exits with a non-zero status code on failure.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/flaccid.git
   cd flaccid
   ```

2. Install dependencies:

   ```bash
   # Run the setup script
   chmod +x setup.sh
   ./setup.sh
   ```

   The setup script will automatically detect whether to use Poetry or pip.

   **Manual installation with Poetry**
   ```bash
   # If you prefer to run the commands manually with Poetry
   poetry install --sync
   ```

   **Manual installation with pip**
   ```bash
   # If you prefer to run the commands manually with pip
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. Configure credentials using environment variables or the `settings store` command, or set up credentials for APIs:

   ```bash
   fla set auth qobuz
   fla set auth apple
   # Both commands prompt for an API key and secret
   # Optional: configure directories
   fla set path --library ~/Music --cache ~/.cache/flaccid
   ```

The Qobuz plugin reads `QOBUZ_APP_ID` and `QOBUZ_TOKEN` from the environment. If the token is invalid it will be refreshed automatically using the stored credentials.

### Plugin Loading

Additional provider plugins can be placed in directories referenced by the `FLACCID_PLUGIN_PATH` environment variable (colon separated). The built-in `PluginLoader` will automatically discover any modules defining subclasses of `MetadataProviderPlugin` and register them for use with the CLI.
Example:

```bash
export FLACCID_PLUGIN_PATH=~/my-flaccid-plugins
fla download custom-provider 1234 song.flac
```
You can control which metadata plugin is preferred when merging fields using the
`PLUGIN_PRECEDENCE` environment variable or via the CLI:

```bash
fla settings precedence qobuz,apple --file settings.toml
```

### Plugin Validation

Validate custom plugins before using them:

```bash
fla plugins validate path/to/plugin.py
```
The command checks for subclasses of `MetadataProviderPlugin` or
`LyricsProviderPlugin` and ensures all required methods are implemented.
## Usage

### Library Scanning

```bash
fla library scan /path/to/music --db library.db --watch
```

### Metadata Tagging

```bash
fla tag fetch /path/to/track.flac --provider qobuz
```

Use the new `fetch` and `apply` commands to manage metadata:

```bash
fla tag fetch /path/to/track.flac --provider qobuz
fla tag apply /path/to/track.flac --metadata-file metadata.json --yes
```
The apply command writes tags using built-in helpers and will attempt to retrieve lyrics automatically when they are missing.
Metadata from different providers is merged using the `cascade` helper so that
missing fields are filled in automatically.

### Database Indexing

```bash
fla lib index --rebuild
fla lib scan /path/to/music --db library.db
```

### Finding and Managing Duplicates

```bash
# Find duplicates by file hash (most accurate)
fla duplicates find ~/Music --by hash

# Find duplicates by title
fla duplicates find ~/Music --by title

# Find duplicates by filename
fla duplicates find ~/Music --by filename --recursive

# Find duplicates by artist and title combination
fla duplicates find ~/Music --by artist+title

# Only consider files larger than 5MB
fla duplicates find ~/Music --min-size 5000

# Export results to JSON file
fla duplicates find ~/Music --export duplicates.json

# Remove duplicates interactively
fla duplicates remove ~/Music --by hash --strategy interactive --no-dry-run

# Automatically keep the highest quality version of each duplicate
fla duplicates remove ~/Music --by hash --strategy keep-highest-quality --no-dry-run

# Keep the newest file of each duplicate set
fla duplicates remove ~/Music --by hash --strategy keep-newest --no-dry-run
```
Sample output for an interactive removal:

```text
$ fla duplicates remove ~/Music --by hash --strategy interactive
🎵 Scanning 200 FLAC files …
🔍 Found 3 duplicate group(s)
📋 2 file(s) will be removed
```
For more help see the [Troubleshooting section](./docs/user-guide.md#troubleshooting).

## Documentation

Comprehensive documentation is available in the [docs/](./docs) directory:

- **[User Guide](./docs/user-guide.md)** - Complete usage guide with examples and troubleshooting
- **[Developer Handbook](./docs/FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md)** - Technical architecture and implementation details
- **[Project Status](./docs/PROJECT_STATUS.md)** - Current implementation status and roadmap
- **[Development Log](./docs/development-log.md)** - Historical development notes and decisions

For quick reference, see the [documentation index](./docs/README.md).

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.


## Running CI Locally

```sh
# Install dependencies
poetry install --sync
# Run linters, type checks, tests
make ci
```

## Versioning

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Release notes are maintained in [CHANGELOG.md](./CHANGELOG.md).

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.
# Last updated: Thu Jul 17 11:47:55 UTC 2025
