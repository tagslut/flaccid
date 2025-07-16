#!/usr/bin/env python3
"""
Legacy entry point script for the FLACCID CLI toolkit.

This is a wrapper that imports and runs the main CLI app.
"""

from flaccid.cli import app

if __name__ == "__main__":
    app()
