#!/bin/bash
set -euo pipefail

# Constants
LOCK_FILE="poetry.lock"
VENV_PATH=".venv"
PYPROJECT_FILE="pyproject.toml"
PYTHON_MIN_VERSION=3.10

# Functions
check_poetry_installed() {
    if command -v poetry &>/dev/null; then
        echo "✅ Poetry is installed."
        return 0
    fi
    echo "⚠️ Poetry is not installed. Falling back to pip."
    return 1
}

resolve_python_binary() {
    echo "🔍 Resolving Python binary (>= $PYTHON_MIN_VERSION)..."
    local PYTHON_BINARIES=("python3.12" "python3.11" "python3.10" "python3")
    for binary in "${PYTHON_BINARIES[@]}"; do
        if command -v "$binary" &>/dev/null; then
            echo "✅ Python binary found: $binary"
            echo "$binary"
            return 0
        fi
    done
    echo "❌ Python 3.10+ is required but not found."
    exit 1
}

verify_lock_file() {
    echo "🔒 Verifying '$LOCK_FILE'..."
    if [ ! -f "$LOCK_FILE" ]; then
        echo "⚠️ Lock file not found. Creating it..."
        poetry lock
    elif ! poetry lock --check &>/dev/null; then
        echo "⚠️ Lock file is out-of-date. Updating it..."
        poetry lock
    else
        echo "✅ Lock file is up-to-date."
    fi
}

setup_poetry() {
    local PYTHON_BINARY="$1"
    echo "📥 Configuring Poetry with Python: $PYTHON_BINARY"
    poetry config virtualenvs.in-project true
    poetry env use "$PYTHON_BINARY"
    verify_lock_file
    echo "📦 Installing dependencies with Poetry..."
    poetry install --sync --no-ansi --with dev
}

setup_pip() {
    echo "📦 Setting up virtual environment with pip..."
    "$PYTHON_BINARY" -m venv "$VENV_PATH"
    local ACTIVATE_PATH
    if [ -f "$VENV_PATH/bin/activate" ]; then
        ACTIVATE_PATH="$VENV_PATH/bin/activate"  # Linux/macOS
    else
        ACTIVATE_PATH="$VENV_PATH/Scripts/activate"  # Windows
    fi
    source "$ACTIVATE_PATH"
    echo "✅ Virtual environment activated."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Main
echo "🚀 Starting FLACCID setup..."
PYTHON_BINARY=$(resolve_python_binary)

if check_poetry_installed; then
    setup_poetry "$PYTHON_BINARY"
else
    setup_pip
fi

echo "✅ FLACCID setup complete!"