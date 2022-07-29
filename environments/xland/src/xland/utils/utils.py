"""
Util functions.
"""

import numpy as np


def convert_to_actual_pos(positions, generated_map):
    """
    Convert 2D locations to 3D coordinates.
    """
    if len(positions) == 0:
        return []

    # Unpack values
    x, y, z = generated_map

    # Set object in the middle of the tile (by adding 0.5)
    n_objects = positions.shape[-1]
    true_positions = np.array(
        [
            [
                (x[tuple(2 * positions[:, i])] + x[tuple(2 * positions[:, i] + 1)]) / 2,
                (y[tuple(2 * positions[:, i])] + y[tuple(2 * positions[:, i] + 1)]) / 2,
                (z[tuple(2 * positions[:, i])] + z[tuple(2 * positions[:, i] + 1)]) / 2,
            ]
            for i in range(n_objects)
        ]
    )

    # We add transpose so that we get N x 3 coordinates (x, y, z for each object)
    return true_positions


def get_bounds(object_type, object_size):
    """
    Returns bounds for certain objects construction.
    """
    if object_type == "box":
        # Assign x, y, z coordinates
        min_v, max_v = -object_size / 4, object_size / 4

        # xMin, xMax, yMin, yMax, zMin, zMax
        return {"bounds": (min_v, max_v, min_v, max_v, min_v, max_v)}

    elif object_type == "capsule":
        return {"radius": object_size / 4, "height": object_size}

    elif object_type == "sphere":
        return {"radius": object_size / 3}

    else:
        raise ValueError
