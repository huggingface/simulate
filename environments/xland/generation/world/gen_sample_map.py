"""
Python code for creating a particular map.
"""

import os
from PIL import Image
import numpy as np


def create_2d_map(name, m, gen_folder, map_format='2x2'):
    # Create the map
    m = np.array(m)

    if map_format == '2x2':
        # Create map
        map_2d = np.zeros((2 * m.shape[0], 2 * m.shape[1], 3), dtype=np.uint8)

        # Read tiles
        tiles = {}
        tiles_folder = os.path.join(gen_folder, 'tiles')
        for tile_pth in os.listdir(tiles_folder):
            if tile_pth.endswith('.png'):
                tiles[tile_pth.split('.')[0]] = np.array(Image.open(os.path.join(tiles_folder, tile_pth)))

        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                map_2d[2*i: 2*(i+1), 2*j:2*(j+1)] = tiles[m[i, j]]
    else:
        # Create map
        map_2d = np.zeros((m.shape[0], m.shape[1], 3), dtype=np.uint8)

        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                
                map_2d[i,j,0] = int(m[i,j][0])
                map_2d[i,j,1] = int(m[i,j][1])
        

    Image.fromarray(map_2d).save(os.path.join(gen_folder, "maps", name + ".png"))

if __name__ == "__main__":

    example_map = [
        ["10", "10", "00", "00", "10", "10", "20", "20", "20"],
        ["10", "10", "00", "10", "10", "20", "20", "20", "20"],
        ["10", "03", "00", "10", "12", "20", "20", "21", "30"],
        ["00", "00", "00", "10", "10", "10", "30", "30", "30"],
        ["00", "00", "01", "10", "10", "10", "00", "00", "00"],
        ["10", "10", "10", "10", "10", "10", "04", "00", "10"],
        ["10", "10", "10", "12", "20", "20", "20", "14", "10"],
        ["10", "10", "10", "10", "10", "20", "20", "20", "20"],
        ["10", "10", "10", "10", "10", "20", "20", "20", "20"],
    ]

    name = "test_map"
    gen_folder = ".gen_files"
    map_format='rgb'
    map_2d = create_2d_map(name, example_map, gen_folder, map_format=map_format)
    
