#!/usr/bin/env python3
"""
FLACCID CLI entry point script.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from flaccid import app

if __name__ == "__main__":
    app()
