#!/bin/bash
set -euo pipefail

README_FILE="README.md"
TMP_FILE="$(mktemp)"
DATE_STR="$(date)"

# 1. Check if the file exists before proceeding
if [ ! -f "$README_FILE" ]; then
  echo "Error: $README_FILE not found."
  exit 1
fi

# 2. Atomically create a new file without any old timestamp lines
grep -v '^# Last updated:' "$README_FILE" > "$TMP_FILE"

# 3. Append a new timestamp to the temporary file
echo "# Last updated: $DATE_STR" >> "$TMP_FILE"

# 4. Replace the original file with the updated one
mv "$TMP_FILE" "$README_FILE"

echo "Updated timestamp in $README_FILE"
