"""
Util functions.
"""

import numpy as np

from simenv.assets.procgen import GRANULARITY


def convert_to_actual_pos(obj_pos, generated_map):
    # Unpack values
    x, y, z = generated_map

    # Get true heights and weights
    true_width, true_height = x.shape
    width, height = true_width / GRANULARITY, true_height / GRANULARITY

    # Get conversiona array to multiply by positions and get indexes on x, y, z
    conversion = np.array([(true_width - 1) / (width), (true_height - 1) / (height)])

    # Set object in the middle of the tile (by adding 0.5)
    converted_pos = np.expand_dims(conversion, axis=1) * [obj_pos + 0.5]

    # Transform to int
    converted_pos = converted_pos.astype(int)

    # Transform to tuple in order to pass to x, y, z
    converted_pos = tuple(*converted_pos)

    return np.array([x[converted_pos], y[converted_pos], z[converted_pos]]).transpose()


def get_bounds(object_type, object_size):
    """
    Returns bounds for certain objects construction.
    """
    if object_type == "Cube":
        # Assign x, y, z coordinates
        min_v, max_v = -object_size / 2, object_size / 2

        # xMin, xMax, yMin, yMax, zMin, zMax
        return {"bounds": (min_v, max_v, min_v, max_v, min_v, max_v)}

    elif object_type == "Cone":
        return {"radius": object_size / 2, "height": object_size}

    elif object_type == "Sphere":
        return {"radius": object_size / 2}

    else:
        raise ValueError
