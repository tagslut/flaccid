#!/bin/bash
set -e

mkdir -p ~/dev/flaccid
cd ~/dev/flaccid

# Create bootstrap.sh with correct quoting
cat <<'EOF' > bootstrap.sh
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
EOF

chmod +x bootstrap.sh

# install_deps.sh
cat <<'EOF' > install_deps.sh
#!/bin/bash
set -e

if ! command -v poetry &> /dev/null; then
  echo "Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

cd flaccid
poetry install
EOF

chmod +x install_deps.sh

# Makefile
cat <<'EOF' > Makefile
install:
	poetry install

setup:
	mkdir -p ~/.flaccid
	cp docs/example_config.toml ~/.flaccid/config.toml || true

test:
	poetry run pytest tests

clean:
	rm -rf dist build *.egg-info

cli:
	poetry run python fla.py --help
EOF

./bootstrap.sh
./install_deps.sh

echo -e "\n✅ FLACCID is ready. Run 'make cli' to begin."
