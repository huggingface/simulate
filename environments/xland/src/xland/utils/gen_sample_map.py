"""
Python code for creating a particular map.
"""

import argparse
import os
from PIL import Image
import numpy as np
import csv

def create_2d_map(name, gen_folder=".gen_files", 
                    benchmarks="benchmark/examples", map_format="2x2"):
    # Create the map
    m = []

    # Read the file with the map
    with open(os.path.join(benchmarks, name + '.csv'), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            m.append(row)
        
    # Transform m to a numpy array
    m = np.array(m)

    if map_format == '2x2':
        # Create map
        # We multiply the shape by two, since, in this case, we are encoding the map
        # as 2x2 tiles
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
        # Create map with tiles 1x1 encoded in first and second channels
        map_2d = np.zeros((m.shape[0], m.shape[1], 3), dtype=np.uint8)

        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                
                map_2d[i,j,0] = int(m[i,j][0])
                map_2d[i,j,1] = int(m[i,j][1])
        

    Image.fromarray(map_2d).save(os.path.join(gen_folder, "maps", name + ".png"))

    
