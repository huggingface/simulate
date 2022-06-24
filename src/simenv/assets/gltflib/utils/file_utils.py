from os import path
from pathlib import Path


def create_parent_dirs(filename: str) -> None:
    """
    Creates any missing parent directories for a given path. For example, given a path like "/a/b/c.jpg", if the
    directories "/a" or "/a/b" do not exist, they will be created.
    :param filename: Path to a file (either relative or absolute)
    """
    Path(path.dirname(filename)).mkdir(parents=True, exist_ok=True)
