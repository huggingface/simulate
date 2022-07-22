.PHONY: quality style test

# Check that source code meets quality standards

quality:
	black --check --line-length 119 --target-version py36 tests src examples environments
	isort --check-only tests src examples environments
	flake8 tests src environments

# Format source code automatically

style:
	black --line-length 119 --target-version py36 tests src examples environments
	isort tests src examples environments

# Run tests for the library

test:
	python -m pytest -n auto --dist=loadfile -s -v  --ignore=tests/test_gltflib/ ./tests/
