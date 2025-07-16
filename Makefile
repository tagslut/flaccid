.PHONY: install setup test clean cli lint fmt ci

install:
	poetry install

setup:
	mkdir -p ~/.flaccid

test:
	poetry run pytest -q -x

lint:
	poetry run flake8 src tests --ignore=E203,E401,E402,F401,F841

fmt:
	poetry run black src tests
# Makefile for FLACCID CLI development

.PHONY: install lint test format ci clean

install:
	@echo "Installing dependencies..."
	poetry install --sync

lint:
	@echo "Running linters..."
	poetry run flake8
	poetry run mypy .

format:
	@echo "Formatting code..."
	poetry run black .
	poetry run isort .

test:
	@echo "Running tests..."
	poetry run pytest

test-simple:
	@echo "Running basic tests only..."
	poetry run pytest tests/unit/test_simple.py tests/unit/utils

ci: format lint test-simple

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache .coverage htmlcov
	@echo "Done!"
clean:
	rm -rf dist build *.egg-info

cli:
	poetry run python -m flaccid --help
# Run formatter followed by linter
style: fmt lint

ci:
	poetry install --sync
	pre-commit run --all-files
	poetry run pytest --cov=flaccid
