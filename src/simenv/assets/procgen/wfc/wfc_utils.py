"""
Utils function for Wave function collapse.
"""

import numpy as np

from ..constants import HEIGHT_CONSTANT


def generate_seed():
    """
    Generate seeds to pass to the C++ side.
    """
    return np.random.randint(0, 2**32, dtype=np.uint32)


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
