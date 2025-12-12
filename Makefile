.PHONY: install test lint format clean build publish

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run ruff format .

clean:
	rm -rf dist
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf safe_kit/__pycache__
	rm -rf tests/__pycache__

build:
	poetry build

publish:
	poetry publish
