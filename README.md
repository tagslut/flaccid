# FLACCID CLI Toolkit

[![CI](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Release](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/flaccid/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/<your-org>/flaccid/badge.svg?branch=main)](https://coveralls.io/github/<your-org>/flaccid?branch=main)

## Overview

FLACCID (FLAC Library and Canonical Content Identification) is a comprehensive CLI toolkit designed for managing and enriching FLAC music libraries. It provides robust metadata enrichment, tagging, and library management features, leveraging APIs like Qobuz, Apple Music, and more.

## Key Features

- **Metadata Enrichment**: Fetch high-quality metadata from multiple sources (Qobuz, Apple Music, etc.).
- **FLAC Tagging**: Apply enriched metadata to FLAC files.
- **Library Management**: Scan, index, and search large music collections.
- **Quality Analysis**: Analyze audio quality distribution.
- **Interactive CLI**: User-friendly commands with rich progress indicators.

## CLI Overview

Common operations use the `flaccid` command:

```bash
flaccid tag fetch <file> --provider qobuz
flaccid tag apply <file> --metadata-file tags.json --yes
flaccid set auth qobuz
flaccid set path --library /mnt/music --cache ~/.cache/flaccid
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
   flaccid set auth qobuz
   flaccid set auth apple
   # Optional: configure directories
   flaccid set path --library ~/Music --cache ~/.cache/flaccid
   ```

## Usage

### Library Scanning

```bash
flaccid lib scan stats /path/to/music --recursive
```

### Metadata Tagging

```bash
flaccid tag qobuz search /path/to/track.flac
```

Use the new `fetch` and `apply` commands to manage metadata:

```bash
flaccid tag fetch /path/to/track.flac --provider qobuz
flaccid tag apply /path/to/track.flac --metadata-file metadata.json --yes
```

### Database Indexing

```bash
flaccid lib index build /path/to/music --recursive
```

## Documentation

For detailed documentation, see the [docs folder](./docs).

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
