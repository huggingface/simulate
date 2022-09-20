.PHONY: quality style test unity-test

# Check that source code meets quality standards

quality:
	black --check --line-length 119 --target-version py36 tests src examples environments integrations/Unity/tests
	isort --check-only tests src examples environments integrations/Unity/tests
	flake8 tests src environments integrations/Unity/tests

# Format source code automatically

style:
	black --line-length 119 --target-version py36 tests src examples environments integrations/Unity/tests
	isort tests src examples environments integrations/Unity/tests

# Run tests for the library

test:
	python -m pytest -n auto --dist=loadfile -s -v  --ignore=tests/test_gltflib/ ./tests/

unity-test:
	python -m pytest -n 8 -s -v  ./integrations/Unity/tests/ --build_exe $(BUILD_EXE)
