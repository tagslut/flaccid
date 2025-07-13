#!/usr/bin/env python3
"""
Run the project's unit test suite.

This helper lets you execute all unit tests with one command:
    python python_tests.py
It discovers the project root automatically (directory containing
this script) and starts pytest in quiet mode (-q).

If you just want the usual verbose pytest runner, run:
    python python_tests.py -v
or simply `pytest` directly from the project root.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys


def main() -> None:
    project_root = pathlib.Path(__file__).resolve().parent
    # Forward *any* extra CLI args the user supplies to pytest
    pytest_args = (
        ["-m", "pytest", *sys.argv[1:]] if sys.argv[1:] else ["-m", "pytest", "-q"]
    )

    exit_code = subprocess.call(
        [sys.executable, *pytest_args],
        cwd=project_root,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
