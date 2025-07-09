#!/bin/bash
set -e

PROJECT_ROOT="$PWD"
MODULES=(get tag lib core shared tests docs)

mkdir -p flaccid
cd flaccid

for m in "${MODULES[@]}"; do
  mkdir -p "$m"
  touch "$m/__init__.py"
done

cat <<PY > fla.py
import typer

app = typer.Typer()

@app.command()
def hello():
    print("FLACCID CLI Bootstrapped.")

if __name__ == "__main__":
    app()
PY

cat <<TOML > pyproject.toml
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
TOML

cat <<GIT > .gitignore
__pycache__/
*.pyc
.env
dist/
build/
*.egg-info
GIT

cd "$PROJECT_ROOT"
echo "Bootstrap complete."
