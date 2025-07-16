#!/bin/bash
set -euo pipefail

function check_poetry() {
    if command -v poetry &> /dev/null; then
        echo "Poetry is installed, using it for dependency management."
        return 0
    else
        echo "Poetry is not installed, falling back to pip."
        return 1
    fi
}

function setup_with_poetry() {
    echo "Installing dependencies with Poetry..."
    poetry install --sync
    echo "Setup complete! You can now use 'poetry run fla' to run commands."
}

function setup_with_pip() {
    echo "Creating virtual environment..."
    python -m venv .venv

    if [ -d ".venv/bin" ]; then
        # Linux/macOS
        source .venv/bin/activate
    else
        # Windows
        source .venv/Scripts/activate
    fi

    echo "Installing dependencies with pip..."
    pip install -r requirements.txt
    pip install -e .

    echo "Setup complete! Activate the virtual environment with:"
    echo "source .venv/bin/activate  # Linux/macOS"
    echo "or"
    echo ".venv\Scripts\activate  # Windows"
    echo "Then you can use 'fla' to run commands."
}

echo "Setting up FLACCID CLI toolkit..."

# Fix pyproject.toml if it has duplicate sections
if [ -f "pyproject.toml" ]; then
    echo "🔍 Checking pyproject.toml for duplicate sections..."

    # Check for duplicate [tool.poetry] sections
    if grep -q "\[tool\.poetry\].*\[tool\.poetry\]" pyproject.toml 2>/dev/null; then
        echo "⚠️ Detected duplicate [tool.poetry] sections in pyproject.toml, fixing..."
        cp pyproject.toml pyproject.toml.bak
        awk 'BEGIN{p=0} /\[tool\.poetry\]/{p++; if(p==1){print; next}} p==1{print} p>1 && /^\[/{p=0; print}' pyproject.toml.bak > pyproject.toml.fixed
        mv pyproject.toml.fixed pyproject.toml
        echo "✅ Fixed [tool.poetry] section"
    fi

    # Check for duplicate dependencies sections
    if grep -q "\[tool\.poetry\.dependencies\].*\[tool\.poetry\.dependencies\]" pyproject.toml 2>/dev/null; then
        echo "⚠️ Detected duplicate [tool.poetry.dependencies] sections, fixing..."
        cp pyproject.toml pyproject.toml.bak
        awk 'BEGIN{p=0} /\[tool\.poetry\.dependencies\]/{p++; if(p==1){print; next}} p==1{print} p>1 && /^\[/{p=0; print}' pyproject.toml.bak > pyproject.toml.fixed
        mv pyproject.toml.fixed pyproject.toml
        echo "✅ Fixed [tool.poetry.dependencies] section"
    fi

    # Check for other common duplicate sections
    for section in "tool\.poetry\.group\.dev\.dependencies" "tool\.mypy" "tool\.pytest\.ini_options" "build-system"; do
        if grep -q "\[$section\].*\[$section\]" pyproject.toml 2>/dev/null; then
            echo "⚠️ Detected duplicate [$section] sections, fixing..."
            cp pyproject.toml pyproject.toml.bak
            awk -v sect="\\[$section\\]" 'BEGIN{p=0} $0 ~ sect {p++; if(p==1){print; next}} p==1{print} p>1 && /^\[/{p=0; print}' pyproject.toml.bak > pyproject.toml.fixed
            mv pyproject.toml.fixed pyproject.toml
            echo "✅ Fixed [$section] section"
        fi
    done
fi

# Determine whether to use Poetry or pip
if check_poetry; then
    setup_with_poetry
else
    setup_with_pip
fi
# Check for Python (prioritize Python 3.12, then 3.11, then 3.10, then any Python 3)
echo "🔍 Checking for Python..."
if command -v python3.12 &>/dev/null; then
    PY_BIN="python3.12"
elif command -v python3.11 &>/dev/null; then
    PY_BIN="python3.11"
elif command -v python3.10 &>/dev/null; then
    PY_BIN="python3.10"
elif command -v python3 &>/dev/null; then
    PY_BIN="python3"
else
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

echo "🐍 Python version: $($PY_BIN --version)"

# Resolve the actual Python binary (avoid pyenv shims that may be broken)
ACTUAL_PY_BIN=$($PY_BIN -Es <<'PY'
import os, sys
print(os.path.realpath(sys.executable))
PY
)

# Check Python version meets requirements (minimum 3.10)
PY_VERSION=$($PY_BIN -Es <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)

# Use awk for version comparison instead of bc which might not be available
PY_VERSION_CHECK=$(awk -v ver="$PY_VERSION" 'BEGIN { print (ver < 3.10) ? "1" : "0" }')
if [[ "$PY_VERSION_CHECK" == "1" ]]; then
    echo "❌ Python 3.10 or higher is required, but $PY_VERSION was found."

    # Check if mise is available and can provide a newer Python
    if command -v mise &>/dev/null; then
        echo "🔍 Checking if mise can provide a newer Python version..."
        if mise ls python | grep -q "3\.1[0-9]\|3\.[2-9][0-9]"; then
            echo "✅ mise has a suitable Python version available"
            echo "⚙️ Setting up mise for this project..."
            # Configure mise to use idiomatic version files
            mise settings add idiomatic_version_file_enable_tools python
            # Create a .python-version file if needed
            echo "3.12" > .python-version
            echo "🔄 Please restart the setup script to use the mise-managed Python version"
            exit 0
        fi
    fi

    exit 1
fi

# Handle special Python installations
if [[ "$ACTUAL_PY_BIN" == *".pyenv"* ]]; then
    echo "⚠️  Detected pyenv shim ($ACTUAL_PY_BIN)."
    # Only fallback to system Python if it meets version requirements
    if command -v /usr/bin/python3 &>/dev/null; then
        SYS_PY_VERSION=$(/usr/bin/python3 -Es <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)
        # Use awk for version comparison
        SYS_VERSION_CHECK=$(awk -v ver="$SYS_PY_VERSION" 'BEGIN { print (ver >= 3.10) ? "1" : "0" }')
        if [[ "$SYS_VERSION_CHECK" == "1" ]]; then
            ACTUAL_PY_BIN="/usr/bin/python3"
            echo "✅ Using system Python $SYS_PY_VERSION at $ACTUAL_PY_BIN"
        else
            echo "✅ Using pyenv Python $PY_VERSION (system Python $SYS_PY_VERSION is too old)"
        fi
    else
        echo "✅ Using pyenv Python $PY_VERSION (no system Python available)"
    fi
fi

# Check if Poetry is installed or install it
if ! command -v poetry &>/dev/null; then
    echo "📥 Poetry not found. Would you like to install Poetry? (y/n)"
    read -r install_poetry
    if [[ "$install_poetry" =~ ^[Yy]$ ]]; then
        echo "⚙️ Installing Poetry..."
        curl -sSL https://install.python-poetry.org | $PY_BIN -

        # Add Poetry to the PATH for this session
        if [[ -d "$HOME/.local/bin" ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        elif [[ -d "$HOME/Library/Python/*/bin" ]]; then  # macOS
            export PATH="$(echo $HOME/Library/Python/*/bin | tr ' ' ':'):$PATH"
        fi

        if ! command -v poetry &>/dev/null; then
            echo "⚠️ Could not find Poetry after installation. Will use pip instead."
            USE_POETRY=false
        else
            echo "✅ Poetry installed successfully"
            USE_POETRY=true
        fi
    else
        echo "⚠️ Poetry installation declined. Will use pip instead."
        USE_POETRY=false
    fi
else
    echo "✅ Poetry is installed"
    poetry --version
    USE_POETRY=true
fi

# Remove pyenv shims from PATH to avoid interpreter confusion
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

# Handle mise warnings about idiomatic version files
if command -v mise &>/dev/null; then
    echo "🔧 Configuring mise idiomatic version files for Python..."
    mise settings add idiomatic_version_file_enable_tools python
    echo "✅ Configured mise to use idiomatic version files for Python"
fi

if [ "$USE_POETRY" = true ]; then
    # Configure Poetry to create venvs in-project
    poetry config virtualenvs.in-project true

    # Set Python interpreter for Poetry to use
    export POETRY_PYTHON="$ACTUAL_PY_BIN"

    echo "🔍 Detecting Poetry environment..."
    POETRY_VERSION=$(poetry --version | awk '{print $3}')
    echo "✅ Using Poetry version $POETRY_VERSION"

    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        echo "❌ pyproject.toml not found. Make sure you're in the correct directory."
        exit 1
    fi

    # Verify lock file is up-to-date
    echo "🔒 Verifying lock file..."
    if [ ! -f "poetry.lock" ]; then
        echo "⚠️ Lock file not found. Creating it..."
        poetry lock
    elif poetry lock --check 2>/dev/null; then
        echo "✅ Lock file up-to-date."
    else
        echo "⚠️ Lock file is out-of-date. Updating..."
        poetry lock
    fi

    echo "📥 Installing dependencies using Poetry..."
    if ! poetry install --sync --no-interaction --with dev; then
        echo "⚠️ Poetry install failed with dev dependencies. Trying without dev..."
        poetry install --sync --no-interaction
    fi

    # Install and run pre-commit hooks if available
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "🔧 Setting up pre-commit hooks..."
        if ! poetry run pre-commit install; then
            echo "⚠️ Failed to install pre-commit hooks. Continuing setup..."
        else
            echo "▶ Running all pre-commit hooks..."
            poetry run pre-commit run --all-files || echo "⚠️ Some pre-commit hooks failed. You may need to fix these issues."
        fi
    fi

    echo "✅ Setup complete! You can now use the CLI with:"
    echo "   poetry run fla [command]"
    echo "   OR"
    echo "   poetry shell"
    echo "   fla [command]"
else
    echo "🔧 Creating virtual environment..."
    $PY_BIN -m venv .venv

    # Handle different shell types
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then  # Windows
        source .venv/Scripts/activate
    else
        echo "❌ Failed to find virtual environment activation script."
        exit 1
    fi

    # Verify activation worked
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        echo "❌ Failed to activate virtual environment."
        exit 1
    fi

    echo "📥 Installing dependencies using pip..."
    python -m pip install --upgrade pip

    # Check if requirements files exist
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing from requirements.txt..."
        python -m pip install -r requirements.txt
    elif [ -f "pyproject.toml" ]; then
        echo "📦 Installing from pyproject.toml using pip..."
        python -m pip install .
    else
        echo "❌ Neither requirements.txt nor pyproject.toml found. Cannot continue."
        exit 1
    fi

    # Install in development mode if setup.py exists
    if [ -f "setup.py" ]; then
        echo "📦 Installing in development mode..."
        python -m pip install -e .
    fi

    # Install development dependencies if available
    if [ -f "requirements-dev.txt" ]; then
        echo "🧪 Installing development dependencies..."
        python -m pip install -r requirements-dev.txt
    fi

    # Install type stubs for better development experience
    echo "🔍 Installing common type stubs..."
    python -m pip install types-PyYAML types-aiohttp types-click types-sqlalchemy || true

    # Install pre-commit if available
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "🔧 Setting up pre-commit hooks..."
        python -m pip install pre-commit
        pre-commit install
        echo "▶ Running all pre-commit hooks..."
        pre-commit run --all-files || echo "⚠️ Some pre-commit hooks failed. You may need to fix these issues."
    fi

    echo "✅ Setup complete! You can now use the CLI with:"
    echo "   source .venv/bin/activate  # or .venv/Scripts/activate on Windows"
    echo "   fla [command]"
fi

# Final check to ensure the CLI is available
if [ "$USE_POETRY" = true ]; then
    if ! poetry run fla --help &>/dev/null; then
        echo "⚠️ Installation completed but 'fla' command is not available."
        echo "   You may need to run: poetry install --sync"
    fi
else
    if ! command -v fla &>/dev/null && [ -n "${VIRTUAL_ENV:-}" ]; then
        echo "⚠️ Installation completed but 'fla' command is not available."
        echo "   You may need to reinstall the package: pip install -e ."
    fi
fi
