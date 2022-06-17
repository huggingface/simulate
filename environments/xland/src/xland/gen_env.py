"""
Python file to call map, game and agents generation.
"""

import simenv as sm

from .utils import convert_to_actual_pos, seed_env
from .world import generate_scene, get_object_pos


def generate_env(
    width,
    height,
    n_objects=3,
    engine=None,
    periodic_output=False,
    specific_map=None,
    sample_map=None,
    seed=None,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    verbose=False,
    show=False,
    tiles=None,
    neighbors=None,
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
        sample_map: The map to sample from.
        seed: The seed to use for the generation of the map.
        N: Size of patterns (WFC param).
        periodic_input: Whether the input is toric (WFC param).
        ground: Whether to use the lowest middle pattern to initialize the bottom of the map (WFC param).
        nb_samples: Number of samples to generate at once (WFC param).
        symmetry: Levels of symmetry to be used when sampling from a map. Values
            larger than one might imply in new tiles, which might be a unwanted behaviour
            (WFC param).
        verbose: whether to print logs or not
        show: Whether to show the map.
        tiles: tiles for simpletiled generation
        neighbors: neighborhood constraints to the tiles
        **kwargs: Additional arguments. Handles unused args as well.

    Returns:
        scene: the generated scene in simenv format.
    """
    seed_env(seed)

    # TODO: choose width and height randomly from a set of predefined values
    # Generate the map if no specific map is passed
    # TODO: create default kwargs to avoid having to do this below:
    nb_tries = kwargs["nb_tries"] if "nb_tries" in kwargs else 10

    # Initialize success and curr_try variables
    success = False
    curr_try = 0

    while not success and curr_try < nb_tries:

        if verbose:
            print("Try {}".format(curr_try + 1))

        # TODO: think about how to optimize, since
        # we only need the map 2d when checking if this map
        # is acceptable or not
        sg = sm.ProcgenGrid(
            width=width,
            height=height,
            specific_map=specific_map,
            sample_map=sample_map,
            tiles=tiles,
            neighbors=neighbors,
            shallow=True,
            algorithm_args={
                "periodic_output": periodic_output,
                "N": N,
                "periodic_input": periodic_input,
                "ground": ground,
                "nb_samples": nb_samples,
                "symmetry": symmetry,
                "verbose": verbose,
            },
        )

        # Get objects position
        threshold_kwargs = {"threshold": kwargs["threshold"]} if "threshold" in kwargs else {}

        # TODO return playable area and use it for agent placement
        # TODO: Add corner case where there are no objects
        obj_pos, success = get_object_pos(sg.map_2d, n_objects=n_objects, **threshold_kwargs)

        # If there is no enough area, we should try again and continue the loop
        if success:
            # Set objects in scene:
            sg.generate_3D()
            obj_pos = convert_to_actual_pos(obj_pos, sg.coordinates)
            scene = generate_scene(sg, obj_pos, engine)

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
        scene.show()
        input("Press Enter to continue...")

        scene.close()

    return success
