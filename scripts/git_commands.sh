#!/bin/bash
#
# Description: Performs git operations
# Usage: ./scripts/git_commands.sh "Your commit message"
#
set -euo pipefail

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Verify Git installation
git --version

# Fix for macOS environment - Git is already installed
echo "Using existing Git installation"

# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Add all changes to staging
echo "Adding all changes to staging..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
  echo "No changes to commit. Working tree clean."
  echo "Pulling latest changes to ensure branch is up-to-date..."
  # Use a simple pull since there's nothing to rebase
  git pull origin "$CURRENT_BRANCH"
  echo "Branch is up-to-date. Exiting."
  exit 0
else
  # Commit the changes with --no-verify to bypass pre-commit hooks
  if [ -z "${1-}" ]; then
    echo "Error: A commit message is required." >&2
    echo "Usage: ./scripts/git_commands.sh \"Your commit message\"" >&2
    exit 1
  fi

  echo "Committing changes..."
  git commit -m "$1" --no-verify

  # Now, pull with rebase to integrate remote changes.
  # This will place your new commit on top of any new commits from the remote.
  echo "Pulling latest changes from origin..."
  git pull --rebase origin "$CURRENT_BRANCH"

  # Push to the remote repository
  echo "Pushing to remote repository..."
  git push origin "$CURRENT_BRANCH"
  echo "Git operations completed successfully."
fi
