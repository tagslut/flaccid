#!/usr/bin/env python3
"""Command-line execution module.

This module allows direct execution of the CLI package with:
    python -m flaccid.cli
"""

from __future__ import annotations

import sys
from flaccid.cli import main

if __name__ == "__main__":
    sys.exit(main())
