"""
Util functions.
"""

import csv
import os

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

    # We add transpose so that we get N x 3 coordinates (x, y, z for each object)
    return np.array([x[converted_pos], y[converted_pos], z[converted_pos]]).transpose()


def get_bounds(object_type, object_size):
    """
    Returns bounds for certain objects construction.
    """
    if object_type == "Box":
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


def create_2d_map(name, benchmarks="benchmark/examples"):
    """
    Create a 2D map from a CSV file with the tiles that should be used in each position.

    Args:
        name: name of the map.
        benchmarks: folder where the benchmark / example files are saved.
    """

    # Create the map
    m = []

    # Read the file with the map
    with open(os.path.join(benchmarks, name + ".csv"), "r") as f:
        reader = csv.reader(f)
        for row in reader:
            m.append(row)

    # Transform m to a numpy array
    m = np.array(m)

    # Create map with tiles 1x1 encoded in first and second channels
    map_2d = np.zeros((m.shape[0], m.shape[1], 3), dtype=np.uint8)

    for i in range(m.shape[0]):
        for j in range(m.shape[1]):

            map_2d[i, j, 0] = int(m[i, j][0])
            map_2d[i, j, 1] = int(m[i, j][1])

    return map_2d
