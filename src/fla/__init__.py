#!/usr/bin/env python3
"""
Legacy *alias* package so that existing code/tests written for the old
namespace ``fla`` continue to work.
"""

from __future__ import annotations

from flaccid import cli
from flaccid.cli import app as cli_app

app = cli.app

__all__ = ["cli_app", "app"]

app = cli.app

__all__ = ["cli_app", "app"]
