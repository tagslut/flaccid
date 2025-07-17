#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script creates a proper CLI entry point for flaccid.
Run it after installing the package to create a working 'fla' script.
"""

import os
import sys
from pathlib import Path


def create_entry_point() -> bool:
    # Get the virtualenv path
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found at .venv")
        return False

    # Create the bin directory if it doesn't exist
    bin_dir = venv_path / "bin"
    bin_dir.mkdir(exist_ok=True)

    # Create the fla script
    fla_path = bin_dir / "fla"

    # Get the Python interpreter path
    python_path = sys.executable

    with open(fla_path, "w") as f:
        f.write(f"""#!/usr/bin/env {python_path}
# -*- coding: utf-8 -*-

import sys
from flaccid.cli.__init__ import main

if __name__ == "__main__":
    sys.exit(main())
""")

    # Make it executable
    os.chmod(fla_path, 0o755)

    print(f"✅ Created entry point at {fla_path}")
    return True


if __name__ == "__main__":
    if create_entry_point():
        print("🎉 Entry point created successfully!")
        print("ℹ️ You can now run 'fla' from the virtual environment.")
    else:
        print("❌ Failed to create entry point.")
