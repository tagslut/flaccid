#!/bin/bash
set -euo pipefail

# Constants
POETRY_CMD="poetry"
PIP_CMD="pip"
LOG_FILE="poetry_script.log"
PYTHON_MIN_VERSION=3.10
COMMAND_TIMEOUT=60  # Reduced timeout to fail faster

# Function: Check if Poetry is installed
check_poetry_installed() {
  if ! command -v $POETRY_CMD &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it." | tee -a "$LOG_FILE"
    exit 1
  fi
  echo "✅ Poetry is installed." | tee -a "$LOG_FILE"
}

# Function: Check if pip is installed
check_pip_installed() {
  if ! command -v $PIP_CMD &> /dev/null; then
    echo "❌ pip is not installed. Please install it." | tee -a "$LOG_FILE"
    exit 1
  fi
  echo "✅ pip is installed." | tee -a "$LOG_FILE"
}

# Function: Resolve Python binary >= 3.10
resolve_python_binary() {
  local versions=("python3.12" "python3.11" "python3.10" "python3")
  for binary in "${versions[@]}"; do
    if command -v "$binary" &> /dev/null; then
      echo "$binary"
      return
    fi
  done
  echo "❌ Python >= 3.10 not found." | tee -a "$LOG_FILE"
  exit 1
}

# Function: Create or activate virtualenv
setup_virtualenv() {
  local python_bin="$1"

  # Create .venv directory if it doesn't exist
  if [ ! -d ".venv" ]; then
    echo "🏗️ Creating new virtual environment with $python_bin..." | tee -a "$LOG_FILE"
    $python_bin -m venv .venv
  fi

  # Activate the virtual environment
  if [ -f ".venv/bin/activate" ]; then
    echo "🔌 Activating virtual environment..." | tee -a "$LOG_FILE"
    source .venv/bin/activate
    return 0
  else
    echo "❌ Failed to create virtual environment." | tee -a "$LOG_FILE"
    return 1
  fi
}

# Function: Export requirements from Poetry
export_requirements() {
  echo "📝 Exporting requirements from Poetry..." | tee -a "$LOG_FILE"

  # Ensure pyproject.toml exists
  if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found." | tee -a "$LOG_FILE"
    return 1
  fi

  # Create a requirements.txt file from pyproject.toml
  if command -v $POETRY_CMD &> /dev/null; then
    echo "📤 Exporting dependencies to requirements.txt..." | tee -a "$LOG_FILE"
    $POETRY_CMD export -f requirements.txt --without-hashes -o requirements.txt 2>> "$LOG_FILE" || {
      echo "⚠️ Poetry export failed, creating basic requirements file..." | tee -a "$LOG_FILE"
      create_basic_requirements
    }

    # Create dev-requirements.txt if dev dependencies exist
    if grep -q "\[tool.poetry.group.dev.dependencies\]" pyproject.toml; then
      echo "📤 Exporting dev dependencies to dev-requirements.txt..." | tee -a "$LOG_FILE"
      $POETRY_CMD export -f requirements.txt --without-hashes --with dev -o dev-requirements.txt 2>> "$LOG_FILE" || {
        echo "⚠️ Poetry dev export failed, creating basic dev requirements file..." | tee -a "$LOG_FILE"
        create_basic_dev_requirements
      }
    fi
  else
    create_basic_requirements
    create_basic_dev_requirements
  fi

  return 0
}

# Function: Create basic requirements from pyproject.toml
create_basic_requirements() {
  echo "📄 Creating basic requirements.txt from pyproject.toml..." | tee -a "$LOG_FILE"

  # Extract dependencies from pyproject.toml
  awk '/\[tool.poetry.dependencies\]/,/\[tool.poetry.group/' pyproject.toml |
  grep -v '\[tool.poetry' |
  grep "=" |
  sed 's/python.*//g' |
  sed 's/^[[:space:]]*//g' |
  sed 's/ = /=/g' |
  sed 's/"//g' |
  sed "s/'//g" |
  sed 's/,//g' |
  grep -v "^$" > requirements.txt
}

# Function: Create basic dev requirements from pyproject.toml
create_basic_dev_requirements() {
  echo "📄 Creating basic dev-requirements.txt from pyproject.toml..." | tee -a "$LOG_FILE"

  # Extract dev dependencies from pyproject.toml
  awk '/\[tool.poetry.group.dev.dependencies\]/,/\[/' pyproject.toml |
  grep -v '\[tool.poetry' |
  grep "=" |
  sed 's/^[[:space:]]*//g' |
  sed 's/ = /=/g' |
  sed 's/"//g' |
  sed "s/'//g" |
  sed 's/,//g' |
  grep -v "^$" > dev-requirements.txt
}

# Function: Install dependencies with pip
install_with_pip() {
  echo "🔄 Falling back to pip for installation..." | tee -a "$LOG_FILE"

  # Ensure we have requirements files
  if [ ! -f "requirements.txt" ]; then
    export_requirements
  fi

  echo "📦 Installing dependencies with pip..." | tee -a "$LOG_FILE"
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt

  if [ -f "dev-requirements.txt" ]; then
    echo "📦 Installing dev dependencies with pip..." | tee -a "$LOG_FILE"
    python -m pip install -r dev-requirements.txt
  fi

  echo "✅ Dependencies installed with pip." | tee -a "$LOG_FILE"
  return 0
}

# Function: Configure Poetry to use the correct environment
configure_poetry_env() {
  local binary="$1"
  echo "🔧 Configuring Poetry environment with $binary..." | tee -a "$LOG_FILE"

  $POETRY_CMD config virtualenvs.in-project true
  $POETRY_CMD env use "$binary"
}

# Function: Execute a command with timeout
run_with_timeout() {
  local cmd="$1"
  local timeout_seconds="$2"

  echo "⏱️ Running with ${timeout_seconds}s timeout: $cmd" | tee -a "$LOG_FILE"

  # Start a subshell for the command
  ($cmd) &
  local pid=$!

  # Wait for the process for a maximum of timeout_seconds
  local count=0
  while kill -0 $pid 2>/dev/null && [ $count -lt $timeout_seconds ]; do
    sleep 1
    ((count++))
  done

  # If the process is still running after the timeout, kill it
  if kill -0 $pid 2>/dev/null; then
    echo "⏱️ Command timed out after ${timeout_seconds}s: $cmd" | tee -a "$LOG_FILE"
    kill -9 $pid 2>/dev/null || true
    return 124  # Return timeout status code
  fi

  # Wait for the process to get its exit code
  wait $pid 2>/dev/null
  return $?
}

# Function: Try Poetry installation
try_poetry_install() {
  echo "🔄 Attempting Poetry installation..." | tee -a "$LOG_FILE"

  # Remove lock file to avoid hanging on outdated locks
  if [ -f "poetry.lock" ]; then
    echo "🔄 Removing poetry.lock file..." | tee -a "$LOG_FILE"
    rm -f poetry.lock
  fi

  # Try to create a new lock file quickly
  echo "🔒 Creating new lock file..." | tee -a "$LOG_FILE"
  if ! run_with_timeout "$POETRY_CMD lock --no-update" 30; then
    echo "⚠️ Poetry lock failed or timed out, proceeding without lock." | tee -a "$LOG_FILE"
  fi

  # Try to install without sync which might be faster
  echo "📦 Installing dependencies with Poetry..." | tee -a "$LOG_FILE"
  if run_with_timeout "$POETRY_CMD install --no-interaction --with dev" 60; then
    echo "✅ Poetry installation succeeded." | tee -a "$LOG_FILE"
    return 0
  fi

  echo "❌ Poetry installation failed or timed out." | tee -a "$LOG_FILE"
  return 1
}

# Main function
main() {
  # Clear or create log file
  > "$LOG_FILE"

  echo "🚀 Starting FLACCID dependency installation..." | tee -a "$LOG_FILE"
  date | tee -a "$LOG_FILE"

  # Check Python and package managers
  check_poetry_installed
  check_pip_installed

  # Resolve Python binary
  local PYTHON_BIN=$(resolve_python_binary)
  echo "🐍 Using Python: $PYTHON_BIN" | tee -a "$LOG_FILE"

  # Set up a virtual environment
  if setup_virtualenv "$PYTHON_BIN"; then
    # Try Poetry first with a short timeout
    configure_poetry_env "$PYTHON_BIN"

    if try_poetry_install; then
      echo "✅ FLACCID dependencies installed successfully with Poetry." | tee -a "$LOG_FILE"
    else
      echo "⚠️ Poetry installation failed, falling back to pip..." | tee -a "$LOG_FILE"

      if install_with_pip; then
        echo "✅ FLACCID dependencies installed successfully with pip." | tee -a "$LOG_FILE"
      else
        echo "❌ Failed to install dependencies with both Poetry and pip." | tee -a "$LOG_FILE"
        exit 1
      fi
    fi
  else
    echo "❌ Failed to set up virtual environment." | tee -a "$LOG_FILE"
    exit 1
  fi

  echo "✅ Installation completed successfully." | tee -a "$LOG_FILE"
  date | tee -a "$LOG_FILE"
}

# Run the main function
main