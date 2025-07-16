!/bin/bash
set -euo pipefail

# Constants
POETRY_CMD="poetry"
LOG_FILE="poetry_script.log"
PYTHON_MIN_VERSION=3.10

# Function: Check if Poetry is installed
check_poetry_installed() {
  if ! command -v $POETRY_CMD &>/dev/null; then
    echo "❌ Poetry is not installed. Please install it." | tee -a "$LOG_FILE"
    exit 1
  fi
  echo "✅ Poetry is installed." | tee -a "$LOG_FILE"
}

# Function: Resolve Python binary >= 3.10
resolve_python_binary() {
  local versions=("python3.12" "python3.11" "python3.10" "python3")
  for binary in "${versions[@]}"; do
    if command -v "$binary" &>/dev/null; then
      echo "$binary"
      return
    fi
  done
  echo "❌ Python >= 3.10 not found." | tee -a "$LOG_FILE"
  exit 1
}

# Function: Configure poetry to use proper env
configure_poetry_env() {
  local binary="$1"
  local resolved=$(command -v "$binary")
  if [[ "$resolved" == "$PWD/.venv"* ]]; then
    echo "⚠️  Skipping venv Python. Falling back to system python3." | tee -a "$LOG_FILE"
    resolved=$(command -v python3)
  fi
  $POETRY_CMD config virtualenvs.in-project true
  $POETRY_CMD env use "$resolved"
}

# Function: Run a Poetry command with logging
run_poetry_command() {
  local command=$1
  echo "▶️ Running: $POETRY_CMD $command" | tee -a "$LOG_FILE"
  $POETRY_CMD $command >> "$LOG_FILE" 2>&1 || {
    echo "❌ Command failed: $command" | tee -a "$LOG_FILE"
    exit 1
  }
}

# Main logic
main() {
  check_poetry_installed
  local PYTHON_BIN=$(resolve_python_binary)
  configure_poetry_env "$PYTHON_BIN"
  run_poetry_command "lock --check || poetry lock"
  run_poetry_command "install --sync --with dev"
  echo "✅ FLACCID dependencies installed successfully." | tee -a "$LOG_FILE"
}

main
