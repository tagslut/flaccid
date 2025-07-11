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
  echo "Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# Print versions for reproducibility
python3 --version
poetry --version

# Tell Poetry to keep the venv local and to use the current python3
poetry config virtualenvs.in-project true
poetry env use "$(command -v python3)"

# 1b. Validate Poetry project
if ! poetry check; then
  echo "❌ Poetry project validation failed. Please fix pyproject.toml."
  exit 1
fi

# 1c. Update lock file if needed, without upgrading dependencies
echo "Ensuring lock file is up to date..."
poetry lock

# 2. Install dependencies
echo "Installing dependencies..."
if ! poetry install --sync --no-interaction --no-ansi --with dev; then
  echo "❌ Poetry install failed."
  exit 1
fi

# 3. Optional deterministic requirements export
poetry export --without-hashes --sort -f requirements.txt -o requirements.txt || true

# 4. Pre-commit hooks
poetry run pre-commit install
poetry run pre-commit clean
echo "▶ Auto-formatting code..."
poetry run black .
poetry run isort .
 # 4b. Auto-remove unused imports (if autoflake is installed)
 if command -v autoflake &>/dev/null; then
   poetry run autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports src tests
 else
   echo "⚠️  autoflake not found; skipping unused-import cleanup"
 fi
if ! poetry run pre-commit run --all-files --show-diff-on-failure; then
  :
fi

# 5. mypy stub auto-install
poetry run mypy --install-types --non-interactive --ignore-missing-imports || true

# 6. Note about integration tests
echo -e "\nℹ️  NOTE: The test suite may include integration tests that require"
echo "   credentials for services like Qobuz or Apple Music."
echo "   If tests fail with connection errors, please configure credentials using:"
echo "   'poetry run fla set auth <service_name>'"

# 6. Run all tests to catch errors early
if poetry run pytest; then
  echo -e "\n✅  Setup complete – activate with 'poetry shell' or run via 'poetry run <cmd>'."
  echo -e "\nUseful commands:"
  echo "  poetry shell            # Activate the virtual environment"
  echo "  poetry run <cmd>       # Run a command inside the venv"
  echo "  poetry run pytest      # Run tests"
  echo "  poetry run pre-commit run --all-files  # Run all pre-commit hooks"
else
  echo -e "\n❌ Tests failed. Please review the errors above."
  exit 1
fi
