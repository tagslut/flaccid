#!/bin/bash

echo "Fixing code issues in the project..."

# Fix duplicate [tool.poetry] section in pyproject.toml
if grep -q "\[tool\.poetry\]" pyproject.toml; then
  echo "Fixing duplicate [tool.poetry] section in pyproject.toml"
  cp pyproject.toml pyproject.toml.bak
  awk '{
    if ($0 == "[tool.poetry]" && seen == 1) {
      exit;
    }
    if ($0 == "[tool.poetry]") {
      seen = 1;
    }
    print;
  }' pyproject.toml.bak > pyproject.toml.fixed
  mv pyproject.toml.fixed pyproject.toml
fi

# Fix setup.py whitespace issue
if [ -f "setup.py" ]; then
  echo "Fixing whitespace in setup.py"
  sed -i '' 's/package_dir={"":"src"}/package_dir={"":"src"}/g' setup.py
fi

# Fix indentation issues in qobuz.py
if [ -f "src/flaccid/plugins/qobuz.py" ]; then
  echo "Fixing indentation in qobuz.py"
  sed -i '' 's/            async def /    async def /g' src/flaccid/plugins/qobuz.py
fi

# Fix return type in metadata.py
if [ -f "src/flaccid/core/metadata.py" ]; then
  echo "Fixing return type in metadata.py"
  sed -i '' 's/-> None:/-> Path:/g' src/flaccid/core/metadata.py
fi

echo "Code fixes completed. Run git_commands.sh to commit and push the changes."
