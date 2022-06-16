"""
Python code for creating a particular map.
"""

import csv
import os

import numpy as np
from PIL import Image


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
