# FLACCID Usage Examples

This guide shows practical examples of the available CLI commands.

## Quick Start

### 1. Store Tokens

Save your service credentials in the system keyring:

```bash
poetry run python -m fla settings store qobuz --token YOUR_QOBUZ_TOKEN
poetry run python -m fla settings store apple --token YOUR_APPLE_TOKEN
```

### 2. Tag Files

Apply Apple Music metadata to a track:

```bash
poetry run python -m fla meta apple /path/to/song.flac 123456789
```

### 3. Download Music

Download tracks from supported services:

```bash
poetry run python -m fla download qobuz 12345678 song.flac
```

### 4. Manage Your Library

```bash
poetry run python -m fla library scan /path/to/music --db library.db
poetry run python -m fla library watch start /path/to/music --db library.db
# later
poetry run python -m fla library watch stop /path/to/music
```

## Environment Configuration

Create a `.env` file and set values such as `QOBUZ_APP_ID`, `QOBUZ_TOKEN`, `APPLE_TOKEN` and other service tokens. The CLI loads these automatically when present.

## CLI Structure

- **`download`** – Download music from Qobuz. Support for Tidal and Beatport is planned.
- **`meta`** – Apply metadata. Currently only Apple Music is implemented.
- **`library`** – Scan folders and build an SQLite index. Includes a `watch` group to monitor changes.
- **`settings`** – Store credentials securely in the keyring.

## Tips

1. Always back up your FLAC files before modifying tags.
2. Use environment variables for API keys when possible.
3. Run commands with `poetry run` during development.

## Troubleshooting

- **Authentication failures** – verify stored tokens with your keyring tool.
- **File access errors** – ensure the process has read/write permissions.
- **API limits** – avoid heavy batch operations that exceed rate limits.

Run any command with `--help` for detailed arguments.
