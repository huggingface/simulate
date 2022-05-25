"""
Python code for creating a particular map.
"""

import os
from PIL import Image
import numpy as np


def create_2d_map(name, m, gen_folder):
    # Read tiles
    tiles = {}
    tiles_folder = os.path.join(gen_folder, 'tiles')
    for tile_pth in os.listdir(tiles_folder):
        if tile_pth.endswith('.png'):
            tiles[tile_pth.split('.')[0]] = np.array(Image.open(os.path.join(tiles_folder, tile_pth)))

    # Create the map
    m = np.array(m)
    map_2d = np.zeros((2 * m.shape[0], 2 * m.shape[1], 3), dtype=np.uint8)

    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            map_2d[2*i: 2*(i+1), 2*j:2*(j+1)] = tiles[m[i, j]]

    print(map_2d.shape)

    Image.fromarray(map_2d).save(os.path.join(gen_folder, "maps", name + ".png"))

if __name__ == "__main__":

    example_map = [
        ["00", "00", "00", "00", "00", "00"],
        ["00", "02", "10", "10", "04", "00"],
        ["00", "10", "10", "10", "00", "00"],
        ["00", "10", "10", "10", "00", "00"],
        ["00", "00", "00", "00", "00", "00"],
        ["00", "00", "00", "00", "00", "00"],
        ["00", "10", "01", "10", "00", "00"],
        ["00", "10", "10", "10", "00", "00"],
        ["00", "20", "20", "11", "00", "00"],
        ["00", "20", "20", "20", "00", "00"],
        ["00", "00", "00", "00", "00", "00"],
    ]

    name = "test_map"
    gen_folder = ".gen_files"
    map_2d = create_2d_map(name, example_map, gen_folder)
    
