set -euo pipefail
echo "🔄 Reinstalling flaccid from source..."
if [ ! -f "setup.py" ]; then
  echo "❌ This script must be run from the project root (where setup.py is located)"
  exit 1
fi
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  echo "🔌 Activating virtual environment..."
  source .venv/bin/activate
fi
echo "🗑️ Uninstalling existing flaccid package..."
pip uninstall -y flaccid || true
echo "📦 Installing flaccid in development mode..."
pip install -e .
echo "🔧 Checking for fla executable..."
FLA_PATH=$(which fla 2>/dev/null || echo "")
if [ -n "$FLA_PATH" ]; then
  PYTHON_PATH=$(command -v python)
  echo "🔧 Updating shebang in $FLA_PATH to use $PYTHON_PATH"
  # Create a temporary file
  TMP_FILE=$(mktemp)
  # Replace the first line with the correct shebang
  echo "#./cleanup.shPYTHON_PATH" > "$TMP_FILE"
  tail -n +2 "$FLA_PATH" >> "$TMP_FILE"
  # Make it executable
  chmod +x "$TMP_FILE"
  # Replace the original file
  sudo mv "$TMP_FILE" "$FLA_PATH"
fi
echo "✅ Installation complete"
echo "🧪 Testing fla command..."
fla --version || echo "⚠️ Command not working yet. Try adding $(pip show -f flaccid | grep bin/fla) to your PATH"
