#!/bin/bash

echo "Fixing pyproject.toml file..."

# Back up the original file
cp pyproject.toml pyproject.toml.bak

# Use awk to remove the second [tool.poetry] section and everything below it
awk '{
  if ($0 == "[tool.poetry]" && seen == 1) {
    exit;
  }
  if ($0 == "[tool.poetry]") {
    seen = 1;
  }
  print;
}' pyproject.toml.bak > pyproject.toml

echo "Fixed pyproject.toml. Original backed up as pyproject.toml.bak"
echo "You can now run git_commands.sh to commit and push your changes."
