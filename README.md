# FLACCID CLI Toolkit

[![CI](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Release](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/<your-org>/flaccid/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/flaccid?branch=main)

## Overview

FLACCID is a simple CLI toolkit for downloading music and enriching FLAC files with metadata. It currently supports Apple Music tagging and downloading tracks from Qobuz, Tidal and Beatport. Library indexing utilities help keep a small SQLite database in sync with your collection.

## Key Features

- **Track Downloads**: `download qobuz|tidal|beatport` saves tracks locally.
- **Metadata Tagging**: `meta apple` applies Apple Music metadata to FLAC files.
- **Library Management**: Scan and watch directories to keep an SQLite index up to date.
- **Credential Storage**: Store service tokens securely in your system keyring.
- **Duplicate Detection**: Find and manage duplicate FLAC files in your library.

## CLI Overview

Run commands via the `fla` module:

```bash
poetry run python -m fla download qobuz 12345678 song.flac
poetry run python -m fla meta apple song.flac 12345678
poetry run python -m fla library scan ~/Music --db library.db
poetry run python -m fla library watch start ~/Music --db library.db
poetry run python -m fla settings store qobuz --token YOUR_TOKEN
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
   # Optional: configure directories
   fla set path --library ~/Music --cache ~/.cache/flaccid
   ```

The Qobuz plugin reads `QOBUZ_APP_ID` and `QOBUZ_TOKEN` from the environment. If the token is invalid it will be refreshed automatically using the stored credentials.
## Usage

### Library Scanning

```bash
fla library scan /path/to/music --db library.db [--watch]  # WIP
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

### Database Indexing

```bash
fla lib index --rebuild  # experimental
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

## Documentation

See [FLACCID CLI Toolkit Developer Handbook](docs/FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md) for architecture details. Additional guides live in the [docs folder](./docs).

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Running CI Locally

```sh
# Install dependencies
poetry install --sync
# Run linters, type checks, tests
make ci
```

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.
# Last updated: Wed Jul 16 07:10:30 EEST 2025
# Last updated: Wed Jul 16 07:11:23 EEST 2025
# Last updated: Wed Jul 16 09:50:57 EEST 2025
# Last updated: Wed Jul 16 09:54:37 EEST 2025
# Last updated: Wed Jul 16 09:59:08 EEST 2025
# Last updated: Wed Jul 16 10:14:34 EEST 2025
# Last updated: Wed Jul 16 10:16:18 EEST 2025
# Last updated: Wed Jul 16 10:20:13 EEST 2025
# Last updated: Wed Jul 16 10:23:57 EEST 2025
# Last updated: Wed Jul 16 10:25:37 EEST 2025
# Last updated: Wed Jul 16 10:29:55 EEST 2025
# Last updated: Wed Jul 16 10:39:34 EEST 2025
# Last updated: Wed Jul 16 10:42:57 EEST 2025
# Last updated: Wed Jul 16 10:43:42 EEST 2025
# Last updated: Wed Jul 16 10:44:34 EEST 2025
# Last updated: Wed Jul 16 10:46:12 EEST 2025
