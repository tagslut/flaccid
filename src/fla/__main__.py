#!/usr/bin/env python3
"""
Shim for legacy `fla` command.

Module to enable `python -m fla` invocation.
Simply delegates to flaccid's CLI app.
"""

from __future__ import annotations

from flaccid.__main__ import main

# Re-export the app for tests that import from here
from flaccid.cli import app  # noqa: F401

if __name__ == "__main__":
    main()
