.PHONY: quality style test

# Check that source code meets quality standards

quality:
	black --check --line-length 119 --target-version py38 .
	isort --check-only tests src
	flake8 .

# Format source code automatically

style:
	black --line-length 119 --target-version py38 .
	isort .

# Run tests for the library

test:
	python -m pytest -n auto --dist=loadfile -s -v ./tests/