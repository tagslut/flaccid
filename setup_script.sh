#!/usr/bin/env bash
set -euo pipefail

# 0. Ensure Python 3 is available
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 is required but not found. Please install Python 3."
  exit 1
fi

# 1. Ensure Poetry is installed
if ! command -v poetry &>/dev/null; then
  echo "⚙️  Poetry not found. Installing..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Print versions
echo "🐍 Python version: $(python3 --version)"
echo "📦 Poetry version: $(poetry --version)"

# 3. Configure Poetry to create venvs in-project
poetry config virtualenvs.in-project true

# 4. Verify lock file is up-to-date
echo "🔒 Verifying lock file..."
if ! poetry lock --check; then
  echo "❌ Lock file out of date. Please run 'poetry lock' and commit the changes."
  exit 1
fi

# 5. Install dependencies (including dev)
echo "📥 Installing dependencies..."
poetry install --sync --no-interaction --no-ansi --with dev

# 6. Install and run pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
poetry run pre-commit install
echo "▶ Running all pre-commit hooks..."
poetry run pre-commit run --all-files --show-diff-on-failure

# 7. Optionally install mypy type stubs
echo "🔍 Installing common type stubs for mypy..."
poetry run pip install --disable-pip-version-check types-PyYAML types-aiohttp types-click types-sqlalchemy || true

echo "✅ Setup complete! To enter the shell: 'poetry shell' or run 'poetry run <cmd>'."