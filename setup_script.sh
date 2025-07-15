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

# Resolve the actual Python binary (avoid pyenv shims that may be broken)
PY_BIN=$(python3 -Es <<'PY'
import os, sys
print(os.path.realpath(sys.executable))
PY
)
# If the resolved path still points inside a pyenv shim directory, fallback to /usr/bin/python3
if [[ "$PY_BIN" == *".pyenv"* ]]; then
  echo "⚠️  Detected pyenv shim ($PY_BIN). Falling back to system Python at /usr/bin/python3."
  PY_BIN="/usr/bin/python3"
fi
export POETRY_PYTHON="$PY_BIN"
poetry env use "$POETRY_PYTHON"  # Set Poetry's Python interpreter *before* PATH adjustments
# --- Remove any pyenv *shims* from PATH to avoid Poetry invoking them ----
if [[ ":$PATH:" == *":$HOME/.pyenv/shims:"* ]] || [[ ":$PATH:" == *":/root/.pyenv/shims:"* ]]; then
  echo "🔧 Removing pyenv shims from PATH to avoid interpreter confusion..."
  # rebuild PATH without any segment that ends with '/.pyenv/shims'
  NEW_PATH=""
  IFS=':' read -ra SEGMENTS <<< "$PATH"
  for seg in "${SEGMENTS[@]}"; do
    [[ "$seg" == */.pyenv/shims ]] && continue
    NEW_PATH="${NEW_PATH:+$NEW_PATH:}$seg"
  done
  export PATH="$NEW_PATH"
fi
# Tell Poetry to use this interpreter for the virtualenv

# 3. Configure Poetry to create venvs in-project
poetry config virtualenvs.in-project true

# 4. Verify lock file is up-to-date (non-fatal)
echo "🔒 Verifying lock file..."
if poetry lock --check; then
  echo "✅ Lock file up-to-date."
else
  echo "⚠️  Could not verify lock file or it is out-of-date. Continuing setup..."
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