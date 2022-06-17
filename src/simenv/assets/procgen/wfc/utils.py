"""
Utils function for Wave function collapse.
"""

import csv
import os

import numpy as np


# Number of divisions for each tile on the mesh
GRANULARITY = 10

# Constant to multiply by the values in the height map to get the actual height
HEIGHT_CONSTANT = 0.6375


def generate_seed():
    """
    Generate seeds to pass to the C++ side.
    """
    return np.random.randint(0, 2**32)


def decode_rgb(img):
    """
    Decode the RGB image into a height map with tiles of 2x2.

    Might be temporary until we migrate completely to this format.
    """

    # Create the map
    map_2d = np.zeros((2 * img.shape[0], 2 * img.shape[1]))

    # TODO: optimize this decoding
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 1] == 0:
                map_2d[2 * i : 2 * (i + 1), 2 * j : 2 * (j + 1)] = img[i, j, 0]
            elif img[i, j, 1] == 1:
                map_2d[2 * i, 2 * j : 2 * (j + 1)] = img[i, j, 0]
                map_2d[2 * i + 1, 2 * j : 2 * (j + 1)] = img[i, j, 0] + 1
            elif img[i, j, 1] == 2:
                map_2d[2 * i : 2 * (i + 1), 2 * j] = img[i, j, 0]
                map_2d[2 * i : 2 * (i + 1), 2 * j + 1] = img[i, j, 0] + 1
            elif img[i, j, 1] == 3:
                map_2d[2 * i, 2 * j : 2 * (j + 1)] = img[i, j, 0] + 1
                map_2d[2 * i + 1, 2 * j : 2 * (j + 1)] = img[i, j, 0]
            elif img[i, j, 1] == 4:
                map_2d[2 * i : 2 * (i + 1), 2 * j] = img[i, j, 0] + 1
                map_2d[2 * i : 2 * (i + 1), 2 * j + 1] = img[i, j, 0]

    map_2d = map_2d * HEIGHT_CONSTANT

    return map_2d


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
