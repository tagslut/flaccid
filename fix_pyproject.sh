#!/bin/bash

echo "Fixing pyproject.toml file..."

# Make a backup of the original file
cp pyproject.toml pyproject.toml.bak

# Create a fixed version that removes the duplicate [tool.poetry] section
awk '{
  if ($0 ~ /^\[tool\.poetry\]/ && seen_poetry == 1) {
    in_duplicate = 1
  } else if (in_duplicate == 1 && $0 ~ /^\[tool\./) {
    in_duplicate = 0
    print $0
  } else if (in_duplicate == 0) {
    print $0
  }
  if ($0 ~ /^\[tool\.poetry\]/ && seen_poetry == 0) {
    seen_poetry = 1
  }
}' pyproject.toml.bak > pyproject.toml.fixed

# Replace the original with the fixed version
mv pyproject.toml.fixed pyproject.toml

echo "pyproject.toml has been fixed. Please verify the changes."
