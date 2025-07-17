# Contributing to FLACCID

Thank you for your interest in improving FLACCID. We welcome bug reports, feature requests and pull requests from everyone.

## Reporting Issues

Please use GitHub Issues to report bugs or request features. Include the steps to reproduce the problem, the expected behavior, the actual behavior and any relevant logs or screenshots.

## Development Setup

1. Fork and clone the repository.
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the test suite and linting:
   ```bash
   poetry run pytest
   poetry run pre-commit run --all-files
   ```
   The pre-commit suite now includes a Vulture hook which fails the build if
   any dead code is detected.
4. If you plan to add a new provider plugin, read the
   [Plugin Development Guide](docs/plugin-development.md) first.

## Pull Requests

1. Create a feature branch from `main`.
2. Make your changes following our code style. We use [black](https://github.com/psf/black) for formatting and run [flake8](https://flake8.pycqa.org/) and [mypy](http://mypy-lang.org/) for linting and type checking.
3. Add or update tests and documentation.
4. Commit your work with descriptive messages and push the branch.
5. Open a pull request referencing any related issues.

## License

By contributing you agree that your contributions are licensed under the project's [GNU General Public License v3.0](LICENSE).
