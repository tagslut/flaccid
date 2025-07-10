#!/usr/bin/env bash
# setup_script.sh - Bootstrap FLACCID dev environment

set -euo pipefail
# Remove stale requirements.txt if present (for clean Poetry export)
rm -f requirements.txt

# 1. Ensure Poetry is installed
if ! command -v poetry &>/dev/null; then
  echo "Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Install Python dependencies (including dev)
echo "Installing Python dependencies with Poetry..."
poetry install --with dev

# Generate requirements.txt for non-Poetry compatibility
echo "Generating requirements.txt from poetry.lock..."
poetry export --without-hashes -f requirements.txt -o requirements.txt || true

# 3. Install pre-commit hooks
echo "Installing pre-commit hooks..."
poetry run pre-commit install

# 4. Clean pre-commit cache and re-run hooks with correct Python version
echo "Cleaning pre-commit cache and running hooks with Python 3.12..."
poetry run pre-commit clean
poetry run pre-commit run --all-files

echo "\nSetup complete! You can now use the FLACCID CLI and run tests."
