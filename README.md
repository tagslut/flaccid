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

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Configure credentials using environment variables or the `settings store` command.

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
