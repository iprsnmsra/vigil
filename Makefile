.PHONY: help install dev test test-unit test-integration lint format docker-build docker-push demo docs clean tf-fmt tf-validate

help:
	@echo "Available targets:"
	@echo "  help             - show all targets"
	@echo "  install          - install all dependencies"
	@echo "  dev              - install dev dependencies"
	@echo "  test             - run all tests"
	@echo "  test-unit        - run unit tests"
	@echo "  test-integration - run integration tests"
	@echo "  lint             - run linters (ruff, mypy)"
	@echo "  format           - run formatters (ruff format)"
	@echo "  docker-build     - build all Docker images"
	@echo "  docker-push      - push images"
	@echo "  demo             - run the local demo"
	@echo "  docs             - serve docs locally"
	@echo "  clean            - clean build artifacts"
	@echo "  tf-fmt           - terraform fmt"
	@echo "  tf-validate      - terraform validate"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

lint:
	ruff check .
	mypy src tests

format:
	ruff format .

docker-build:
	docker build -t vigil:latest .

docker-push:
	docker push vigil:latest

demo:
	python -m vigil.demo

docs:
	mkdocs serve

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist *.egg-info

tf-fmt:
	terraform fmt -recursive

tf-validate:
	terraform validate
