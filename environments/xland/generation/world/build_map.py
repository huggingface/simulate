"""
Builds map using Wave Function Collapse.

NOTE: This file is still a draft.
"""

import os
from .gen_tiles import generate_tiles
import numpy as np
import simenv as sm
from PIL import Image
import wfc_binding


def generate_2d_map(seed, width, height, gen_folder):
    """
    TODO: implement this function to have a binding with c++
    """
    # TODO: Open image if it's cached

    # Otherwise, generate it:
    wfc_binding.py_main(width, height)
    img_path = os.path.join(gen_folder, 'maps/tiles.png')

    # Read file
    img = Image.open(img_path) 
    return img


def generate_map(seed, 
                width, 
                height, 
                tile_size=10, 
                gen_folder=".gen_files",
                or_tile_size=2,
                height_constant=0.2):
    """
    Generate the map.

    Args:
        seed: The seed to use for the generation of the map.
        width: The width of the map.
        height: The height of the map.
        tile_size: The size of the resulting tiles.
        gen_folder: where to find all generation-necessary files.
        or_tile_size: The size of the tiles in the original image.

    NOTE: This is a draft.
    """

    img = generate_2d_map(seed, width, height, gen_folder)

    img_np = np.array(img)
    img_np = img_np[:,:,0] * height_constant

    # First we will just extract the map and plot
    z_grid = img_np 

    # Let's say we want tiles of tile_size x tile_size pixels, and a certain "size" on number
    # of tiles:
    # TODO: change variables and make this clearer
    # TODO: make rectangular shapes possible

    # Number of divisions for each tile on the mesh
    granularity = 10

    x = np.arange(- width * tile_size // 2, width * tile_size // 2, tile_size / granularity)
    y = np.arange(- height * tile_size // 2, height * tile_size // 2, tile_size / granularity)

    x, y = np.meshgrid(x, y)

    # create z_grid
    z_grid = np.zeros(x.shape)

    # TODO: improve performance of this loop
    for i in range(height):
        for j in range(width):
            img_val = img_np[i * or_tile_size:(i + 1) * or_tile_size, j * or_tile_size:(j + 1) * or_tile_size]

            # generating for one axis
            grid = np.transpose(np.linspace(img_val[0], img_val[1], granularity))

            # now for other
            grid = np.transpose(np.linspace(grid[0], grid[1], granularity))

            z_grid[i * granularity:(i + 1) * granularity, j * granularity:(j + 1) * granularity] = grid

    floor = sm.StructuredGrid(x=x, y=y, z=z_grid)
    floor.plot()

