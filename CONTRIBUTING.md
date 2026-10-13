# Contributing to Vigil

Thank you for investing your time in contributing to our project!

## Setting up your dev environment
1. Ensure Python 3.11+ is installed.
2. Clone the repository and run `make dev` to install development dependencies.
3. Install pre-commit hooks via `pre-commit install`.

## Running tests
Run `make test` to execute the full test suite.
For specific tests, use `make test-unit` or `make test-integration`.

## Submitting Pull Requests
1. Fork the repo and create your branch from `main`.
2. Ensure your PR passes all CI checks.
3. We use Conventional Commits (e.g., `feat: added feature`, `fix: squashed bug`).

## Code Style
This project uses `ruff` for formatting and linting, and `mypy` for static type checking.
Run `make lint` and `make format` before submitting.
