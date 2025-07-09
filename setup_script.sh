#!/usr/bin/env bash
# setup_script.sh - Bootstrap FLACCID dev environment
set -euo pipefail

# 1. Ensure Poetry is installed
if ! command -v poetry &>/dev/null; then
  echo "Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Install Python dependencies (including dev)
echo "Installing Python dependencies with Poetry..."
poetry install --with dev

# 3. Install pre-commit hooks
echo "Installing pre-commit hooks..."
poetry run pre-commit install

# 4. Run all pre-commit hooks once
echo "Running all pre-commit hooks..."
poetry run pre-commit run --all-files

echo "\nSetup complete! You can now use the FLACCID CLI and run tests."
