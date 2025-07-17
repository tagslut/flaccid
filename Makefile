.PHONY: test lint build release docs coverage ci

# Run unit tests
test:
	poetry run pytest -q

# Run all linters and type checks
lint:
	poetry run pre-commit run --all-files

# Build distributable packages
build:
	poetry build

# Publish a release to PyPI
release:
	poetry publish --no-interaction

# Build documentation (placeholder)
docs:
	@echo "Documentation lives in docs/"

# Generate coverage report
coverage:
	poetry run pytest --cov=src --cov-report=html

# Run full CI pipeline locally
ci: lint coverage
