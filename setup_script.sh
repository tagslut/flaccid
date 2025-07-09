#!/usr/bin/env bash
# setup_script.sh - Bootstrap FLACCID dev environment

set -euo pipefail
# Temporary fallback to avoid early pip install failures
touch requirements.txt

# 1. Ensure Poetry is installed
if ! command -v poetry &>/dev/null; then
  echo "Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Install Python dependencies (including dev)
echo "Installing Python dependencies with Poetry..."
poetry install --with dev

# Generate requirements.txt if missing (for non-Poetry compatibility)
if [ ! -f requirements.txt ]; then
  echo "Generating requirements.txt from poetry.lock..."
  poetry export --without-hashes -f requirements.txt -o requirements.txt || true
fi

# 3. Install pre-commit hooks
echo "Installing pre-commit hooks..."
poetry run pre-commit install

# 4. Clean pre-commit cache and re-run hooks with correct Python version
echo "Cleaning pre-commit cache and running hooks with Python 3.12..."
poetry run pre-commit clean
poetry run pre-commit run --all-files

echo "\nSetup complete! You can now use the FLACCID CLI and run tests."
