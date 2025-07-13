# FLACCID CLI Toolkit

[![CI](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Release](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/<your-org>/flaccid/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/flaccid?branch=main)

## Overview

FLACCID is a comprehensive CLI toolkit designed for managing and enriching FLAC music libraries. It provides robust metadata enrichment, tagging, and library management features, leveraging APIs like Qobuz, Tidal, Apple Music, Discogs, Beatport and more.

## Key Features

- **Metadata Enrichment**: Fetch high-quality metadata from multiple sources (Qobuz, Tidal, Apple Music, Discogs, Beatport, etc.).
- **FLAC Tagging**: Apply enriched metadata to FLAC files.
- **Lyrics Embedding**: Optionally fetch and embed lyrics using a lyrics plugin.
- **Library Management**: Scan, index, and search large music collections.
- **Quality Analysis**: Analyze audio quality distribution *(planned)*.
- **Interactive CLI**: User-friendly commands with rich progress indicators.
- **Plugin System**: Easily extend support for new services via modular plugins *(in progress)*.
- **Streamlined Tagging Workflow**: `fla tag <provider>` fetches and writes metadata in one step.
- **Library Indexing**: `fla lib scan` and `fla lib index` maintain a searchable SQLite database *(WIP)*.

## CLI Overview

Common operations use the `fla` command:

```bash
fla tag fetch <file> --provider qobuz
fla tag apply <file> --metadata-file tags.json --yes
fla set auth qobuz
fla set path --library /mnt/music --cache ~/.cache/flaccid
fla get qobuz <track_id> output.flac
```
If the download fails, the command exits with an error message and a non-zero status code.

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
fla library scan /path/to/music --db library.db
fla library watch start /path/to/music --db library.db
# later...
fla library watch stop /path/to/music
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
The apply command writes tags using built-in helpers and will attempt to
retrieve lyrics automatically when they are missing. Metadata providers like
Qobuz and Apple Music are accessed through modules in ``flaccid.tag`` which
wrap the underlying plugin APIs.

### Database Indexing

```bash
fla lib index --rebuild  # experimental
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

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.
