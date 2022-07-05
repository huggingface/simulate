"""
Generate tiles for debugging purposes, and for generating maps on the prototype.
"""

import numpy as np

from .constants import HEIGHT_CONSTANT


def img_from_tiles():
    """
    Transform tiles into an unique image for tile visualization.
    """
    raise NotImplementedError


def get_tile(h, orientation=0):
    """
    Returns plain tile of height h of a certain orientation.
    """
    if orientation == 0:
        return np.full((2, 2), h * HEIGHT_CONSTANT)
    else:
        return np.rot90(np.array([[0, 0], [1, 1]]), orientation - 1) * HEIGHT_CONSTANT


def generate_tiles(max_height=6, double_ramp=False):
    """
    Generate tiles for the procedural generation.
    NOTE: So far, we are using these values to get used to how to use the algorithm.

    Args:
        max_height: can be any integer between 1 and 256 (and it's advisable to use a power of 2, to avoid
            approximation errors).
        weights: weights for each of the levels of height. If none, defaults for a linear decay between [10, 0.2]
        double_ramp: whether double ramps should be allowed or not.

    Returns:
        tiles, neighbors
    """

    # TODO: which should be default weights?
    plain_weights = np.exp(np.linspace(1.0, -3.0, max(6, max_height)))[:max_height]
    ramp_weights = [0.2] * max_height

    # Step for the height (which is represented by the intensity of the color)
    tiles = []
    symmetries = []
    weights = []
    neighbors = []

    # Generate tiles
    for h in range(max_height):

        # Generate plain tile
        tiles.append(get_tile(h))

        # Symmetry of a certain letter means that it has the sames symmetric
        # as the letter
        symmetries.append("X")
        weights.append(plain_weights[h])
        neighbors.append((tiles[-1], tiles[-1]))

        # If i == max_height - 1, then we don't add more ramps
        if h < max_height - 1:

            # Add transition from upper tiles to downer tiles
            neighbors.append((get_tile(h + 1), get_tile(h)))

            # Generation of ramp tiles:
            # Here we only generate from bottom to top, right to left, left to right
            # and top to bottom, in this order
            for i in range(0, 2):
                for ax in range(0, 2):
                    # Ramp orientation (more details down here)
                    ramp_or = i * 2 + ax
                    tiles.append(get_tile(h, ramp_or + 1))
                    symmetries.append("L")
                    weights.append(ramp_weights[h])

                    # We add neighbors
                    # Notice that we have to add orientation
                    # The tiles are rotate clockwise as i * 2 + ax increases
                    # And we add a rotation to fix that and keep the ramps in the right place
                    neighbors.append((get_tile(h, ramp_or + 1), get_tile(h), ramp_or, 0))
                    neighbors.append((get_tile(h + 1), get_tile(h, ramp_or + 1), 0, ramp_or))

                    # Adding ramp to going upwards
                    if h < max_height - 2 and double_ramp:
                        neighbors.append((get_tile(h + 1, ramp_or + 1), get_tile(h, ramp_or + 1), ramp_or, ramp_or))

    return np.array(tiles), np.array(symmetries), np.array(weights), neighbors
