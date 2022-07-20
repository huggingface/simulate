"""
Python file to call map, game and agents generation.
"""

import simenv as sm

from .utils import seed_env
from .world import generate_scene, get_positions


def create_scene(
    width,
    height,
    n_objects=3,
    n_agents=1,
    engine=None,
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
    executable=None,
    port=None,
    headless=None,
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
        n_agents: number of agents to be set in the map.
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
        tiles: tiles for simpletiled generation
        neighbors: neighborhood constraints to the tiles
        symmetries: level of symmetry for each of the tiles. See ProcgenGrid description for more details.
        weights: sampling weights for each of the tiles
        executable: engine executable path
        port: port to be used to communicate with the engine
        headless: whether to run the engine in headless mode
        **kwargs: Additional arguments. Handles unused args as well.
    Returns:
        scene: the generated scene in simenv format.
    """

    seed_env(seed)

    # TODO: choose width and height randomly from a set of predefined values
    # Initialize success and curr_try variables
    success = False
    curr_try = 0
    scene = None
    nb_tries = kwargs.get("nb_tries", 10)

    while not success and curr_try < nb_tries:
        
        if verbose:
            print("Try {}".format(curr_try + 1))
        
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
            sg.map_2d, n_objects=n_objects, n_agents=n_agents, threshold=kwargs.get("threshold", 0.5)
        )

        # If there is no enough area, we should try again and continue the loop
        if success:
            # Set objects in scene:
            scene = generate_scene(
                sg,
                obj_pos,
                agent_pos,
                engine=engine,
                executable=executable,
                port=port,
                headless=headless,
                verbose=verbose,
                physics_update_rate = kwargs.get("physics_update_rate", 30),
                frame_skip = kwargs.get("frame_skip", 4),
            )

            # Generate the game
            # generate_game(generated_map, scene)

        else:
            curr_try += 1

            if seed is not None:
                # Change to seed to test other maps
                seed += 1
            
    return success, scene
