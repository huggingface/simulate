"""
Python file to call map, game and agents generation.
"""

import simulate as sm

from .utils import seed_env
from .world import generate_map, get_positions


def create_map(
    rank,
    width,
    height,
    n_objects=3,
    n_agents=1,
    periodic_output=False,
    specific_map=None,
    sample_map=None,
    seed=None,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=4,
    verbose=False,
    tiles=None,
    symmetries=None,
    weights=None,
    neighbors=None,
    predicate="random",
    **kwargs,
):
    """
    Generate the environment root: map, game and agents.
    Notice that all parameters with the tag WFC param means that they passed
    to the C++ implementation of Wave Function Collapse.
    Args:
        width: The width of the map.
        height: The height of the map.
        n_objects: number of objects to be set in the map.
        n_agents: number of agents to be set in the map.
        periodic_output: Whether the output should be toric (WFC param).
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
        tiles: tiles for simpletiled generation
        neighbors: neighborhood constraints to the tiles
        symmetries: level of symmetry for each of the tiles. See ProcgenGrid description for more details.
        weights: sampling weights for each of the tiles
        predicate: type of predicate (random or None)
        **kwargs: Additional arguments. Handles unused args as well.
    Returns:
        root: the generated map root in simulate format.
    """

    seed_env(seed)

    # Initialize success and attempt variables
    success = False
    attempt = 0
    nb_attempts = kwargs.get("nb_attempts", 10)

    while not success and attempt < nb_attempts:

        if verbose:
            print("Attempt {}".format(attempt + 1))

        sg = sm.ProcgenGrid(
            width=width,
            height=height,
            specific_map=specific_map,
            sample_map=sample_map,
            tiles=tiles,
            symmetries=symmetries,
            weights=weights,
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

        # Get objects and agents positions
        obj_pos, agent_pos, success = get_positions(
            sg.map_2d,
            n_objects=n_objects,
            n_agents=n_agents,
            verbose=verbose,
            threshold=kwargs.pop("threshold", 0.5),
            enforce_lower_floor=kwargs.pop("enforce_lower_floor", True),
        )

        # If there is no enough area, we should try again and continue the loop
        if success:
            # Set objects in scene:
            root = generate_map(
                sg,
                obj_pos,
                agent_pos,
                rank=rank,
                predicate=predicate,
                camera_width=kwargs.pop("camera_width", 96),
                camera_height=kwargs.pop("camera_height", 72),
                object_type=kwargs.pop("object_type", None),
                specific_color=kwargs.pop("specific_color", None),
                n_options=kwargs.pop("n_options", 1),
                n_conjunctions=kwargs.pop("n_conjunctions", 2),
            )

        else:
            attempt += 1

            if seed is not None:
                # Change to seed to test other maps
                seed += 1
    if success:
        return root

    return None
