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

# Tell Poetry to keep the venv local and to use the current python3
poetry config virtualenvs.in-project true
poetry env use "$(command -v python3)"

# 2. Install dependencies
echo "Installing dependencies..."
poetry install --with dev

# 3. Optional deterministic requirements export
poetry export --without-hashes --sort -f requirements.txt -o requirements.txt || true

# 4. Pre-commit hooks
poetry run pre-commit install
poetry run pre-commit clean
if ! poetry run pre-commit run --all-files; then
  echo "❌ pre-commit hooks failed. Fix issues and re-run setup."
  exit 1
fi

# 5. mypy stub auto-install
poetry run mypy --install-types --non-interactive || true

# 6. Run all tests to catch errors early
if poetry run pytest; then
  echo -e "\n✅  Setup complete – activate with 'poetry shell' or run via 'poetry run <cmd>'."
else
  echo -e "\n❌ Tests failed. Please review the errors above."
  exit 1
fi
