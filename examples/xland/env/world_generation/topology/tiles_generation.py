import numpy as np

HEIGHT_CONSTANT = 0.75

def get_tile(h, orientation=0):
    """
    Returns plain tile of height h of a certain orientation.
    """
    if orientation == 0:
        return np.full((2, 2), h * HEIGHT_CONSTANT)
    else:
        return np.rot90(np.array([[h, h], [h + 1, h + 1]]), orientation - 1) * HEIGHT_CONSTANT

def generate_tiles_settings(max_height=6, double_ramp=True):
    """
    Generate tiles for the procedural generation.

    Args:
        max_height: can be any integer between 1 and 256 (and it's advisable to use a power of 2, to avoid
            approximation errors).
        double_ramp: whether double ramps should be allowed or not.

    Returns:
        Dict(tiles, symmetries, weights, neighbors)
    """
    plain_weights = [2.0] * max_height
    border_weights = [2.0] * max_height
    corner_weights = [0.5] * max_height
    ramp_weights = [4.] * max_height

    tiles = []
    symmetries = []
    weights = []
    neighbors = []

    # Generate tiles
    for h in range(max_height):
        # Generate plain tile
        tiles.append(
            {
                "name": f"plain_{h}",
                "image": get_tile(h)
             })
        symmetries.append("X")
        weights.append(plain_weights[h])
        if h > 0:
            # Generate border tile
            tiles.append(
                {
                    "name": f"border_{h}",
                    "image": get_tile(h)
                })
            symmetries.append("T")
            weights.append(border_weights[h])
            # Generate corner tile
            tiles.append(
                {
                    "name": f"corner_{h}",
                    "image": get_tile(h)
                })
            symmetries.append("L")
            weights.append(corner_weights[h])
            for _i in range(h):
                neighbors.append((f"border_{h}", f"plain_{_i}", 1, 0))
                neighbors.append((f"corner_{h}", f"plain_{_i}", 1, 0))
                neighbors.append((f"border_{h}", f"border_{_i}", 1, 1))
                neighbors.append((f"corner_{h}", f"border_{_i}", 1, 1))

            neighbors.append((f"border_{h}", f"border_{h}"))
            neighbors.append((f"border_{h}", f"corner_{h}", 2, 2))
            neighbors.append((f"plain_{h}", f"border_{h}", 0, 1))
            neighbors.append((f"plain_{h}", f"corner_{h}", 0, 1)) # Remove this when diag tiles are added

        neighbors.append((f"plain_{h}", f"plain_{h}"))

        if h < max_height - 1:
            tiles.append(
                {
                    "name": f"ramp_{h}",
                    "image": get_tile(h, 1)
                })
            symmetries.append("L")
            weights.append(ramp_weights[h])
            neighbors.append((f"border_{h + 1}", f"ramp_{h}", 1, 3))
            neighbors.append((f"corner_{h + 1}", f"ramp_{h}", 1, 3))
            neighbors.append((f"ramp_{h}", f"plain_{h}", 3, 0))
            neighbors.append((f"ramp_{h}", f"border_{h}", 3, 1))
            neighbors.append((f"ramp_{h}", f"corner_{h}", 3, 1))

        #     # Adding ramp to going upwards
        #     if h < max_height - 2 and double_ramp:
        #         neighbors.append((get_tile(h + 1, 1), get_tile(h, 1), 0, 0))

    return {
        "tiles": tiles,
        "symmetries": np.array(symmetries),
        "weights": np.array(weights),
        "neighbors": neighbors
    }