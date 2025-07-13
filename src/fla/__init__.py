"""
Legacy *alias* package so that existing code/tests written for the old
namespace ``fla`` continue to work.
"""

from __future__ import annotations

from flaccid import cli

app = cli.app
