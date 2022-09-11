.PHONY: quality style test unity-test

# Check that source code meets quality standards

quality:
	black --check --line-length 119 --target-version py36 tests src examples environments integrations
	isort --check-only tests src examples environments integrations
	flake8 tests src environments integrations

# Format source code automatically

style:
	black --line-length 119 --target-version py36 tests src examples environments integrations
	isort tests src examples environments integrations

# Run tests for the library

test:
	python -m pytest -n auto --dist=loadfile -s -v  --ignore=tests/test_gltflib/ ./tests/

unity-test:
	python -m pytest -n 1 -s -v  ./integrations/Unity/tests/ --build_exe $(BUILD_EXE)
