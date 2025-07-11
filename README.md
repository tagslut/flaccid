# FLACCID CLI Toolkit

[![CI](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Release](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/<your-org>/flaccid/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/flaccid?branch=main)

## Overview

FLACCID is a comprehensive CLI toolkit designed for managing and enriching FLAC music libraries. It provides robust metadata enrichment, tagging, and library management features, leveraging APIs like Qobuz, Apple Music, and more.

## Key Features

- **Metadata Enrichment**: Fetch high-quality metadata from multiple sources (Qobuz, Apple Music, etc.).
- **FLAC Tagging**: Apply enriched metadata to FLAC files.
- **Library Management**: Scan, index, and search large music collections.
- **Quality Analysis**: Analyze audio quality distribution.
- **Interactive CLI**: User-friendly commands with rich progress indicators.
- **Plugin System**: Easily extend support for new services via modular plugins.
- **Streamlined Tagging Workflow**: `fla tag <provider>` fetches and writes metadata in one step.
- **Library Indexing**: `fla lib scan` and `fla lib index` maintain a searchable SQLite database.

## CLI Overview

Common operations use the `fla` command:

```bash
fla tag fetch <file> --provider qobuz
fla tag apply <file> --metadata-file tags.json --yes
fla set auth qobuz
fla set path --library /mnt/music --cache ~/.cache/flaccid
fla get qobuz <track_id> output.flac
```

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

3. Set up credentials for APIs:

   ```bash
   fla set auth qobuz
   fla set auth apple
   # Optional: configure directories
   fla set path --library ~/Music --cache ~/.cache/flaccid
   ```

## Usage

### Library Scanning

```bash
fla lib scan /path/to/music --db library.db
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

### Database Indexing

```bash
fla lib index --rebuild
fla lib scan /path/to/music --db library.db
```

## Documentation

For architectural details such as the plugin system, tagging workflow, and library indexing, see [FLACCID CLI Toolkit Developer Handbook](docs/FLACCID%20CLI%20Toolkit%20Developer%20Handbook.md). Additional guides are available in the [docs folder](./docs).

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

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
