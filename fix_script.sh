set -euo pipefail
echo "🔧 Fixing fla script..."
FLA_PATH=".venv/bin/fla"
if [ ! -f "$FLA_PATH" ]; then
  echo "❌ fla script not found at $FLA_PATH"
  exit 1
fi
echo "📝 Fixing script format..."
cat > "$FLA_PATH" << 'EOFINNER'
import sys
import os
import re
from flaccid.cli.__init__ import main
if __name__ == "__main__":
    sys.exit(main())
EOFINNER
chmod +x "$FLA_PATH"
echo "✅ Script fixed!"
echo "🧪 Testing fla command..."
if [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi
.venv/bin/fla --version || echo "⚠️ Command still not working. You may need to create a proper entry point script."
