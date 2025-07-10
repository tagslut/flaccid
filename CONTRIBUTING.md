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

## Reporting Issues
- Use GitHub Issues to report bugs or request features.
- Please provide as much detail as possible, including steps to reproduce and relevant logs.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
