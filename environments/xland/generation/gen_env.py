"""
Python file to call map, game and agents generation.
"""

import os
from world import generate_map, generate_tiles
from game import generate_game


def gen_setup(gen_folder=".gen_files"):
    """
    Setup the generation.
    """
    # Check if tiles exist
    # Create the folder that stores tiles and maps if it doesn't exist.
    if not os.path.exists(gen_folder):
        os.makedirs(gen_folder)
    
    # Create the maps and tiles folder if necessary
    maps_folder = os.path.join(gen_folder, "maps")
    tiles_folder = os.path.join(gen_folder, 'tiles')

    if not os.path.exists(maps_folder):
        os.makedirs(maps_folder)

    if os.path.exists(tiles_folder):
        print("Tiles folder already exists. Using existing tiles... (delete folder to regenerate)")
    
    else:
        os.makedirs(tiles_folder)
        generate_tiles()


def generate_env(seed, width, height, periodic_output=False, specific_map=None):
    """
    Generate the environment.
    """

    # TODO: choose width and height randomly from a set of predefined values
    # Generate the map if no specific map is passed
    generate_map(seed=seed, width=width, height=height, specific_map=specific_map)


    # Generate the game
    generate_game()

    # TODO: generation of agents


if __name__ == '__main__':
    seed = 0
    width = 12
    height = 8
    periodic_output = True
    specific_map = "test_map.png"
    sample_from = None

    gen_setup()
    generate_env(seed, width, height, periodic_output=periodic_output, specific_map=specific_map)