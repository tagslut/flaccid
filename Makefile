PYTHON := $(shell command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)

.PHONY: setup poetry venv check-python pre-commit

setup: check-python poetry pre-commit
	@echo "✅ FLACCID CLI setup complete."

check-python:
	@echo "🐍 Using Python at: $(PYTHON)"
	@$(PYTHON) --version

poetry:
ifeq (, $(shell command -v poetry))
	@echo "📥 Installing Poetry..."
	@curl -sSL https://install.python-poetry.org | $(PYTHON) -
	@export PATH="$$HOME/.local/bin:$$PATH"
endif
	poetry config virtualenvs.in-project true
	poetry env use $(PYTHON)
	poetry install --sync --no-interaction --with dev

venv:
	@$(PYTHON) -m venv .venv
	@. .venv/bin/activate && pip install -e . && pip install -r requirements.txt

pre-commit:
ifneq (,$(wildcard .pre-commit-config.yaml))
	@poetry run pre-commit install || echo "⚠️ Pre-commit install failed."
	@poetry run pre-commit run --all-files || echo "⚠️ Some pre-commit hooks failed."
endif
