.PHONY: install setup test clean cli lint fmt

install:
	poetry install

setup:
	mkdir -p ~/.flaccid
	cp docs/example_config.toml ~/.flaccid/config.toml || true

test:
	poetry run python python_tests.py -q -x

lint:
	poetry run flake8 src tests --ignore=E203,E401,E402,F401,F841

fmt:
	poetry run black src tests

clean:
	rm -rf dist build *.egg-info

cli:
	poetry run python fla.py --help
# Run formatter followed by linter
style: fmt lint