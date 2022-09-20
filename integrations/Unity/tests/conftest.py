import socket

import pytest


def pytest_addoption(parser):
    parser.addoption("--build_exe", action="store", help="path to Unity build")


@pytest.fixture(scope="session")
def port_number(worker_id):
    """use a different port in each xdist worker"""
    port = 56000 + hash(worker_id) % 1024
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", port)) == 0:
            port = 58000 + hash(worker_id) % 1024  # test another port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", port)) == 0:
                    raise Exception("No available port found")
    return port


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
