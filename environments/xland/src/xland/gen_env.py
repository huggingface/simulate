"""
Python file to call map, game and agents generation.
"""

import os

from .utils import convert_to_actual_pos
from .world import create_objects, generate_map, generate_tiles, get_object_pos


def gen_setup(max_height=8, gen_folder=".gen_files"):
    """
    Setup the generation.

    Args:
        max_height: The maximum height of the map.
        gen_folder: The folder to store the generation files.
    """
    # Check if tiles exist
    # Create the folder that stores tiles and maps if it doesn't exist.
    if not os.path.exists(gen_folder):
        os.makedirs(gen_folder)

    # Create the maps and tiles folder if necessary
    maps_folder = os.path.join(gen_folder, "maps")
    tiles_folder = os.path.join(gen_folder, "tiles")

    if not os.path.exists(maps_folder):
        os.makedirs(maps_folder)

    if os.path.exists(tiles_folder):
        print("Tiles folder already exists. Using existing tiles... (delete folder to regenerate)")

    else:
        os.makedirs(tiles_folder)
        generate_tiles(max_height=max_height)


def generate_env(
    width,
    height,
    n_objects=3,
    engine=None,
    periodic_output=False,
    specific_map=None,
    sample_from=None,
    seed=None,
    max_height=8,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    verbose=False,
    show=False,
    **kwargs,
):
    """
    Generate the environment: map, game and agents.

    Notice that all parameters with the tag WFC param means that they passed
    to the C++ implementation of Wave Function Collapse.

    Args:
        width: The width of the map.
        height: The height of the map.
        n_objects: number of objects to be set in the map.
        periodic_output: Whether the output should be toric (WFC param).
        engine: which engine to use.
        specific_map: A specific map to be plotted.
        sample_from: The name of the map to sample from.
        seed: The seed to use for the generation of the map.
        max_height: The maximum height of the map. Max height of 8 means 8 different levels.
        N: Size of patterns (WFC param).
        periodic_input: Whether the input is toric (WFC param).
        ground: Whether to use the lowest middle pattern to initialize the bottom of the map (WFC param).
        nb_samples: Number of samples to generate at once (WFC param).
        symmetry: Levels of symmetry to be used when sampling from a map. Values
            larger than one might imply in new tiles, which might be a unwanted behaviour
            (WFC param).
        verbose: whether to print logs or not
        show: Whether to show the map.
        **kwargs: Additional arguments. Handles unused args as well.

    Returns:
        scene: the generated scene in simenv format.
    """

    # TODO: choose width and height randomly from a set of predefined values
    # Generate the map if no specific map is passed
    nb_tries = kwargs["nb_tries"] if "nb_tries" in kwargs else 10

    # Initialize success and curr_try variables
    success = False
    curr_try = 0

    while not success and curr_try < nb_tries:

        if verbose:
            print("Try {}".format(curr_try + 1))

        # TODO: add sucess variable to be returned below
        generated_map, map_2d, scene = generate_map(
            width=width,
            height=height,
            periodic_output=periodic_output,
            specific_map=specific_map,
            sample_from=sample_from,
            seed=seed,
            max_height=max_height,
            N=N,
            periodic_input=periodic_input,
            ground=ground,
            nb_samples=nb_samples,
            symmetry=symmetry,
            engine=engine,
        )

        # Get objects position
        threshold = kwargs["threshold"] if "threshold" in kwargs else None
        threshold = 0.1
        obj_pos, success = get_object_pos(map_2d, n_objects=n_objects, threshold=threshold)

        # If there is no enough area, we should try again and continue the loop
        # TODO: improve quality of this code
        if success:
            # Set objects in scene:
            obj_pos = convert_to_actual_pos(obj_pos, generated_map)
            scene += create_objects(obj_pos)

            # Generate the game
            # generate_game(generated_map, scene)

            # TODO: generation of agents

        else:
            curr_try += 1
            if seed is not None:
                # Change to seed to test other maps
                seed += 1

    # If we want to show the map and we were successful
    if show and success:
        # TODO: set camera properly
        scene.show(in_background=False)

    return scene, success
