#!/bin/bash
# Script to fix common issues in pyproject.toml files

set -euo pipefail

if [ ! -f "pyproject.toml" ]; then
    echo "❌ No pyproject.toml file found in the current directory!"
    exit 1
fi

echo "🔍 Checking pyproject.toml for issues..."

# Create backup
cp -f pyproject.toml pyproject.toml.bak
echo "✅ Created backup at pyproject.toml.bak"

# Fix duplicate sections
for section in "tool\.poetry" "tool\.poetry\.dependencies" "tool\.poetry\.group\.dev\.dependencies" "tool\.mypy" "tool\.pytest\.ini_options" "build-system" "tool\.black"; do
    if grep -q "\[$section\].*\[$section\]" pyproject.toml 2>/dev/null; then
        echo "⚠️ Detected duplicate [$section] sections, fixing..."
        awk -v sect="\\[$section\\]" 'BEGIN{p=0} $0 ~ sect {p++; if(p==1){print; next}} p==1{print} p>1 && /^\[/{p=0; print}' pyproject.toml > pyproject.toml.fixed
        mv pyproject.toml.fixed pyproject.toml
        echo "✅ Fixed [$section] section"
    fi
done

# Fix inconsistent Python version requirements
python_ver_main=$(grep -oP '\[tool\.poetry\.dependencies\][^[]*python\s*=\s*"[\^>=]*\K[0-9]+' pyproject.toml | head -1)
python_ver_full=$(grep -oP '\[tool\.poetry\.dependencies\][^[]*python\s*=\s*"\K[\^>=]*[0-9]+(\.[0-9]+)*' pyproject.toml | head -1)

if [ -n "$python_ver_main" ] && [ -n "$python_ver_full" ]; then
    echo "🔍 Found main Python requirement: $python_ver_full"

    # Update mypy python_version
    if grep -q "\[tool\.mypy\]" pyproject.toml; then
        sed -i -E "s/(\[tool\.mypy\][^[]*python_version\s*=\s*\")[0-9]+(\.[0-9]+)*(\")/\1$python_ver_main\3/g" pyproject.toml
        echo "✅ Updated mypy python_version to match dependencies"
    fi

    # Update black target-version
    if grep -q "\[tool\.black\]" pyproject.toml; then
        sed -i -E "s/(target-version\s*=\s*\[[^]]*'py)[0-9]+(\')[^]]*\]/\1$python_ver_main\2]/g" pyproject.toml
        echo "✅ Updated black target-version to match dependencies"
    fi
fi

# Configure mise to handle Python version files
if command -v mise &>/dev/null; then
    echo "🔧 Configuring mise for Python version files..."
    mise settings add idiomatic_version_file_enable_tools python
    echo "✅ Configured mise to use idiomatic version files for Python"
fi

echo "✨ pyproject.toml cleanup complete!"
echo "ℹ️ You can run 'poetry check' to verify the file is now valid."
