#!/bin/bash
set -e

BASE_DIR=~/dev/flaccid
SRC_DIR="$BASE_DIR/src"
PKG_DIR="$SRC_DIR/flaccid"

echo "📁 Creating directory structure..."
mkdir -p "$PKG_DIR"/{get,tag,lib,core,shared,tests,docs}
touch "$PKG_DIR"/{__init__.py,get/__init__.py,tag/__init__.py,lib/__init__.py,core/__init__.py,shared/__init__.py,tests/__init__.py,docs/__init__.py}

echo "📝 Writing fla.py..."
cat > "$SRC_DIR/fla.py" <<EOF
import typer
from flaccid import get

app = typer.Typer(help="FLACCID CLI Toolkit")
app.add_typer(get.app, name="get")

if __name__ == "__main__":
    app()
EOF

echo "📝 Writing get/__init__.py..."
cat > "$PKG_DIR/get/__init__.py" <<EOF
import typer
from . import qobuz

app = typer.Typer(name="get", help="Download music from supported services.")
app.add_typer(qobuz.app, name="qobuz", help="Download music from Qobuz.")
EOF

echo "📝 Writing get/qobuz.py..."
cat > "$PKG_DIR/get/qobuz.py" <<EOF
import typer

app = typer.Typer(help="Qobuz downloader")

@app.command()
def track(id: str):
    \"""
    Download a track by Qobuz track ID.
    \"""
    print(f"🔻 Simulated download for Qobuz track ID: {id}")
EOF

echo "📝 Writing pyproject.toml..."
cat > "$BASE_DIR/pyproject.toml" <<EOF
[tool.poetry]
name = "flaccid"
version = "0.1.0"
description = "Modular FLAC CLI Toolkit"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
typer = "^0.12.3"
pydantic = "^2.6"
dynaconf = "^3.2"
aiohttp = "^3.9"
keyring = "^25.2"
mutagen = "^1.47"
rich = "^13.6"
sqlalchemy = "^2.0"
watchdog = "^4.0"

[[tool.poetry.packages]]
include = "flaccid"
from = "src"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

echo "📦 Setting up Poetry..."
cd "$BASE_DIR"
poetry install

echo "✅ FLACCID CLI scaffolded. Try it:"
echo "    poetry run python src/fla.py get qobuz track --id 123456"
