# FLACCID CLI Toolkit

## Overview

FLACCID (FLAC Library and Canonical Content Identification) is a comprehensive CLI toolkit designed for managing and enriching FLAC music libraries. It provides robust metadata enrichment, tagging, and library management features, leveraging APIs like Qobuz, Apple Music, and more.

## Key Features

- **Metadata Enrichment**: Fetch high-quality metadata from multiple sources (Qobuz, Apple Music, etc.).
- **FLAC Tagging**: Apply enriched metadata to FLAC files.
- **Library Management**: Scan, index, and search large music collections.
- **Quality Analysis**: Analyze audio quality distribution.
- **Interactive CLI**: User-friendly commands with rich progress indicators.

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
   ```

## Usage

### Library Scanning

```bash
fla lib scan stats /path/to/music --recursive
```

### Metadata Tagging

```bash
fla tag qobuz search /path/to/track.flac
```

### Database Indexing

```bash
fla lib index build /path/to/music --recursive
```

### Tagging Files

The `tag` command allows you to apply metadata to FLAC files. It validates the file path before proceeding.

#### Example Usage

```bash
# Tag a file
fla tag /path/to/track.flac

# Handle missing paths
fla tag /path/to/nonexistent.flac
# Output: Path not found
```

## Documentation

For detailed documentation, see the [docs folder](./docs).

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
