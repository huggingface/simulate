"""
Python file to call map, game and agents generation.
"""

import os
from .world import generate_map, generate_tiles
from .game import generate_game


def gen_setup(max_height, gen_folder=".gen_files"):
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
        generate_tiles(max_height=max_height)


def generate_env(width, height, periodic_output=False, specific_map=None, sample_from=None, seed=None,
                    max_height=8, N=2, periodic_input=False, ground=False, nb_samples=1, symmetry=1,
                    show=False, **kwargs):
    """
    Generate the environment.
    """

    # TODO: choose width and height randomly from a set of predefined values
    # Generate the map if no specific map is passed
    generated_map, map_2d, scene = generate_map(width=width, height=height, periodic_output=periodic_output,
                specific_map=specific_map, sample_from=sample_from, seed=seed, max_height=max_height, N=N, 
                periodic_input=periodic_input, ground=ground, nb_samples=nb_samples, symmetry=symmetry)

    # Generate the game
    # generate_game(generated_map, scene)

    # TODO: generation of agents

    if show:
        scene.show(in_background=False)
    
    return scene
