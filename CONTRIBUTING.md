# Contributing to FLACCID

Thank you for your interest in contributing to FLACCID! We welcome contributions of all kinds, including bug reports, feature requests, code, and documentation improvements.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Install dependencies** using Poetry:
   ```bash
   poetry install
   ```
3. **Run the test suite** to ensure everything works:
   ```bash
   poetry run pytest
   ```
4. **Make your changes** following the project’s code style (enforced by pre-commit hooks).
5. **Add or update tests** as needed.
6. **Document your changes** in the appropriate markdown files (e.g., `README.md`, `docs/`).
7. **Commit and push** your changes, then open a pull request.

## Code Style & Quality
- Use [black](https://github.com/psf/black) for formatting.
- Use [flake8](https://flake8.pycqa.org/) and [mypy](http://mypy-lang.org/) for linting and type checking.
- All code must pass pre-commit hooks. Run:
  ```bash
  poetry run pre-commit run --all-files
  ```

## Project Structure
- Source code: `src/flaccid/`
- Tests: `tests/`
- Documentation: `README.md`, `docs/`
# Contributing to FLACCID CLI Toolkit

Thank you for considering contributing to the FLACCID CLI Toolkit! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any relevant logs or screenshots

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

- A clear, descriptive title
- A detailed description of the proposed feature
- Any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Development Setup

1. Clone the repository
2. Install dependencies with Poetry or pip (see README.md)
3. Make your changes
4. Run tests with `pytest`
5. Run linting with `flake8`
6. Run type checking with `mypy`

## Code Style

We follow the [Black](https://github.com/psf/black) code style. Please ensure your code is formatted with Black before submitting a pull request.

```bash
black src tests
```

We also use type hints throughout the codebase. Please add appropriate type hints to any new code.

## Testing

Please add tests for any new features or bug fixes. We use pytest for testing.

```bash
pytest
```

## Documentation

Please update the documentation when adding or changing features. This includes:

- Docstrings for new functions, classes, and methods
- Updates to README.md if needed
- Updates to any relevant documentation in the docs directory

## Commit Messages

Please write clear, descriptive commit messages that explain the changes you've made.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [GNU General Public License v3.0](LICENSE).
## Reporting Issues
- Use GitHub Issues to report bugs or request features.
- Please provide as much detail as possible, including steps to reproduce and relevant logs.

## License
By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.
