#!/bin/bash
set -euo pipefail

# Constants
POETRY_CMD="poetry"
LOG_FILE="poetry_script.log"
PYTHON_MIN_VERSION=3.10
COMMAND_TIMEOUT=300  # 5 minutes timeout for commands

# Function: Check if Poetry is installed
check_poetry_installed() {
  if ! command -v $POETRY_CMD &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it." | tee -a "$LOG_FILE"
    exit 1
  fi
  echo "✅ Poetry is installed." | tee -a "$LOG_FILE"
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

# Function: Configure Poetry to use the correct environment
configure_poetry_env() {
  local binary="$1"
  local resolved=$(command -v "$binary")
  if [[ "$resolved" == "$PWD/.venv"* ]]; then
    echo "⚠️  Skipping venv Python. Falling back to system python3." | tee -a "$LOG_FILE"
    resolved=$(command -v python3)
  fi
  echo "Using Python: $resolved" | tee -a "$LOG_FILE"
  $POETRY_CMD config virtualenvs.in-project true
  $POETRY_CMD env use "$resolved"
}

# Function: Clean up environment if stuck
cleanup_environment() {
  echo "🧹 Cleaning up environment to resolve stuck installation..." | tee -a "$LOG_FILE"

  # Remove poetry.lock if it exists
  if [ -f "poetry.lock" ]; then
    echo "  - Removing poetry.lock file" | tee -a "$LOG_FILE"
    rm -f poetry.lock
  fi

  # Clear Poetry cache
  echo "  - Clearing Poetry cache" | tee -a "$LOG_FILE"
  $POETRY_CMD cache clear --all pypi >> "$LOG_FILE" 2>&1 || true

  # Remove virtual environment if it exists
  if [ -d ".venv" ]; then
    echo "  - Removing existing virtual environment" | tee -a "$LOG_FILE"
    rm -rf .venv
  fi

  # Disable parallel installer
  echo "  - Disabling parallel installer" | tee -a "$LOG_FILE"
  $POETRY_CMD config experimental.new-installer false

  echo "✅ Environment cleanup completed" | tee -a "$LOG_FILE"
}

# Function: Execute a command with timeout
run_with_timeout() {
  local cmd="$1"
  local timeout_seconds="$2"

  if command -v timeout &> /dev/null; then
    timeout "$timeout_seconds" $cmd
    return $?
  elif command -v gtimeout &> /dev/null; then
    gtimeout "$timeout_seconds" $cmd
    return $?
  else
    # Fallback if timeout command is not available
    $cmd &
    local pid=$!

    # Wait for process to finish or timeout
    (
      sleep "$timeout_seconds"
      kill -9 $pid 2>/dev/null || true
    ) &
    local watchdog=$!

    wait $pid 2>/dev/null || true
    local exit_code=$?

    # Kill the watchdog
    kill -9 $watchdog 2>/dev/null || true

    if [ $exit_code -ne 0 ]; then
      if kill -0 $pid 2>/dev/null; then
        # Process still running, must be timeout
        kill -9 $pid 2>/dev/null || true
        return 124  # timeout exit code
      fi
    fi
    return $exit_code
  fi
}

# Function: Execute a Poetry command with timeout and retries
execute_poetry_command_with_timeout() {
  local cmd="$1"
  local timeout_seconds="$2"
  local attempts="$3"

  echo "▶️ Running: $POETRY_CMD $cmd" | tee -a "$LOG_FILE"

  for attempt in $(seq 1 $attempts); do
    echo "  Attempt $attempt of $attempts..." | tee -a "$LOG_FILE"

    # Use timeout command to prevent hanging
    if run_with_timeout "$POETRY_CMD $cmd" "$timeout_seconds" >> "$LOG_FILE" 2>&1; then
      echo "✅ Command succeeded: $cmd" | tee -a "$LOG_FILE"
      return 0
    else
      exit_code=$?
      if [ $exit_code -eq 124 ]; then
        echo "⚠️  Command timed out after ${timeout_seconds}s: $cmd" | tee -a "$LOG_FILE"

        if [ $attempt -lt $attempts ]; then
          echo "🔄 Performing cleanup and retrying..." | tee -a "$LOG_FILE"
          cleanup_environment
        else
          echo "❌ Max attempts reached. Command failed: $cmd" | tee -a "$LOG_FILE"
          return 1
        fi
      else
        echo "❌ Command failed with exit code $exit_code: $cmd" | tee -a "$LOG_FILE"
        if [ $attempt -lt $attempts ]; then
          echo "🔄 Retrying..." | tee -a "$LOG_FILE"
          cleanup_environment
        else
          return 1
        fi
      fi
    fi
  done

  return 1
}

# Function: Install with fallback if Poetry fails
install_dependencies() {
  # First try with Poetry lock
  echo "🔒 Updating lock file..." | tee -a "$LOG_FILE"
  if ! execute_poetry_command_with_timeout "lock" $COMMAND_TIMEOUT 1; then
    echo "⚠️ Poetry lock failed, proceeding without lock" | tee -a "$LOG_FILE"
  fi

  # Try Poetry install with three attempts, cleaning up between each
  if execute_poetry_command_with_timeout "install --with dev -v" $COMMAND_TIMEOUT 3; then
    echo "✅ Poetry successfully installed dependencies" | tee -a "$LOG_FILE"
    return 0
  fi

  # Try without --sync which can cause hanging
  echo "⚠️ Trying installation without --sync flag..." | tee -a "$LOG_FILE"
  if execute_poetry_command_with_timeout "install --with dev -v" $COMMAND_TIMEOUT 1; then
    echo "✅ Poetry successfully installed dependencies (without --sync)" | tee -a "$LOG_FILE"
    return 0
  fi

  echo "❌ Poetry installation failed after multiple attempts." | tee -a "$LOG_FILE"
  echo "⚠️ Please try running 'poetry install -v' manually to see detailed errors." | tee -a "$LOG_FILE"
  return 1
}

# Main logic
main() {
  # Clear previous log
  > "$LOG_FILE"

  check_poetry_installed
  local PYTHON_BIN=$(resolve_python_binary)
  configure_poetry_env "$PYTHON_BIN"

  if install_dependencies; then
    echo "✅ FLACCID dependencies installed successfully." | tee -a "$LOG_FILE"
  else
    echo "❌ Failed to install dependencies. See $LOG_FILE for details." | tee -a "$LOG_FILE"
    exit 1
  fi
}

main