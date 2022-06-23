"""Python wrapper for constructors of C++ classes."""

from wfc_binding import build_neighbor, build_tile


def build_wfc_neighbor(left, right, left_or=0, right_or=0):
    """
    Builds neighbors.
    """
    return build_neighbor(left=bytes(left, "UTF_8"), left_or=left_or, right=bytes(right, "UTF_8"), right_or=right_or)


def build_wfc_tile(tile, name, symmetry="L", weight=1, size=0):
    """
    Builds ties.
    """
    return build_tile(
        size=size, tile=tile, name=bytes(name, "UTF_8"), symmetry=bytes(symmetry, "UTF_8"), weight=weight
    )
