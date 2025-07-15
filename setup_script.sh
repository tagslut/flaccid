#!/usr/bin/env bash
# setup_script.sh - Bootstrap FLACCID dev environment

set -euo pipefail
# Uncomment for debug: set -x

# 0. Check for Python 3
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 is required but not found. Please install Python 3."
  exit 1
fi

# Remove stale requirements.txt if present (for clean Poetry export)
rm -f requirements.txt

# 1. Ensure Poetry is installed
if ! command -v poetry &>/dev/null; then
  echo "⚙️  Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# Print versions for reproducibility
python3 --version
poetry --version

# Tell Poetry to keep the venv local and to use the default python3 in PATH
poetry config virtualenvs.in-project true
poetry env use python3 || echo "⚠️ Unable to pin environment; using default Poetry venv"

# 1b. Validate Poetry project
if ! poetry check; then
  echo "❌ Poetry project validation failed. Please fix pyproject.toml."
  exit 1
fi

# 1c. Update lock file if needed, without upgrading dependencies
echo "🔒 Ensuring lock file is up to date..."
poetry lock

# 2. Install dependencies
echo "📦 Installing dependencies..."
if ! poetry install --sync --no-interaction --no-ansi --with dev; then
  echo "❌ Poetry install failed."
  exit 1
fi

# 3. Optional deterministic requirements export
echo "📝 Exporting requirements.txt for external tools..."
poetry export --without-hashes --sort -f requirements.txt -o requirements.txt || true

# 4. Pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
poetry run pre-commit install
poetry run pre-commit gc
echo "▶ Running all pre-commit hooks to format and check the code..."
if ! poetry run pre-commit run --all-files --show-diff-on-failure; then
  echo -e "\n❌ Pre-commit hooks failed. Please review the errors above."
  exit 1
fi

# 5. mypy stub auto-install
echo "▶ Installing common type stubs for mypy..."
poetry run pip install --disable-pip-version-check types-click types-sqlalchemy || true
poetry run mypy --install-types --non-interactive --ignore-missing-imports || true

# 6. Note about integration tests
echo -e "\nℹ️  NOTE: Some integration tests may require credentials for services like Qobuz or Apple Music."
echo "   If tests fail with connection errors, configure credentials via:"
echo "     poetry run flaccid set auth <service_name>"

# 7. Final notes
echo -e "\n✅  Setup complete! Activate your environment with:"
echo "      poetry shell"
echo "   or run commands directly via:"
echo "      poetry run <cmd>"
echo -e "\nUseful commands:"
echo "  poetry run pytest                      # Run the full test suite"
echo "  poetry run pre-commit run --all-files  # Re-run all pre-commit checks"