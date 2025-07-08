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
