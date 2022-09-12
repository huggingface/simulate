import pytest


def pytest_addoption(parser):
    parser.addoption("--build_exe", action="store", help="path to Unity build")


@pytest.fixture(scope="session")
def build_exe(pytestconfig):
    value = pytestconfig.getoption("build_exe")
    if value is None:
        raise ValueError("Please provide a path to the Unity build executable")
    return value


@pytest.fixture(scope="session")
def set_mpl():
    """Avoid matplotlib windows popping up."""
    try:
        import matplotlib
    except Exception:
        pass
    else:
        matplotlib.use("agg", force=True)
