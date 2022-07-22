import pyvista
from pytest import fixture


pyvista.OFF_SCREEN = True


@fixture(scope="session")
def set_mpl():
    """Avoid matplotlib windows popping up."""
    try:
        import matplotlib
    except Exception:
        pass
    else:
        matplotlib.use("agg", force=True)
