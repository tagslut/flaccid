set -euo pipefail
echo "🔧 Fixing Python interpreter path in fla CLI executable..."
FLA_PATH=$(which fla 2>/dev/null || echo "")
if [ -z "$FLA_PATH" ]; then
  echo "❌ fla executable not found in PATH"
  # Try to find it in common locations
  for loc in "$HOME/Library/Python/3.11/bin/fla" "$HOME/Library/Python/3.10/bin/fla" "$HOME/.local/bin/fla"; do
    if [ -f "$loc" ]; then
      FLA_PATH="$loc"
      echo "🔍 Found fla at: $FLA_PATH"
      break
    fi
  done
  if [ -z "$FLA_PATH" ]; then
    echo "❌ Could not find fla executable"
    exit 1
  fi
fi
echo "📝 Current shebang line:"
head -n 1 "$FLA_PATH"
PYTHON_PATH=$(command -v python3 || command -v python)
if [ -z "$PYTHON_PATH" ]; then
  echo "❌ Python interpreter not found"
  exit 1
fi
echo "🐍 Using Python at: $PYTHON_PATH"
TMP_FILE=$(mktemp)
echo "#./reinstall.shPYTHON_PATH" > "$TMP_FILE"
tail -n +2 "$FLA_PATH" >> "$TMP_FILE"
chmod +x "$TMP_FILE"
sudo mv "$TMP_FILE" "$FLA_PATH"
echo "✅ Fixed shebang in $FLA_PATH"
echo "📝 New shebang line:"
head -n 1 "$FLA_PATH"
echo "🧪 Testing fla command..."
fla --version || echo "⚠️ Command not working yet. You may need to reinstall."
