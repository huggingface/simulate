"""
Minimal script for generating a map.

In this instance, we don't interact with the environment but rather just show it.
"""

import argparse
import time
from collections import defaultdict

from xland import create_scene
from xland.utils import create_2d_map, generate_tiles


ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Check create_scene for more information about the arguments where
    # `help`` is not provided
    # Main arguments are the following:
    parser.add_argument("--show", type=bool, default=False, help="Show the map")
    parser.add_argument("--verbose", type=bool, default=False, help="Verbose for debugging")
    parser.add_argument("--width", type=int, default=8, help="Width of generated map")
    parser.add_argument("--height", type=int, default=10, help="Height of generated map")
    parser.add_argument("--n_objects", type=int, default=3, help="Number of objects to be placed in the scene")
    parser.add_argument("--n_agents", type=int, default=1, help="Number of agents to be placed in the scene")
    parser.add_argument("--seed", type=int, default=None, help="Seed for random number generator")
    parser.add_argument("--sample_from", type=str, default=None, help="Map to sample from")
    parser.add_argument("--map", type=str, default=None, help="Specific map to be used")
    parser.add_argument("--engine", type=str, default=None, help="Engine to be used")

    # Optional arguments which are related to WFC
    parser.add_argument("--periodic_output", type=bool, default=True)
    parser.add_argument("--periodic_input", type=bool, default=True)
    parser.add_argument("--ground", type=bool, default=False)
    parser.add_argument("--max_height", type=int, default=6)
    parser.add_argument("--symmetry", type=int, default=1)
    parser.add_argument("--N", type=int, default=2)
    parser.add_argument("--nb_samples", type=int, default=1)

    args = parser.parse_args()
    extra_args = defaultdict(lambda: None)

    if args.sample_from is None and args.map is None:
        tiles, neighbors = generate_tiles(args.max_height)
        extra_args["tiles"] = tiles
        extra_args["neighbors"] = neighbors

    else:
        name = args.map or args.sample_from
        m = create_2d_map(name)
        if args.map is not None:
            extra_args["specific_map"] = m
        else:
            extra_args["sample_map"] = m

    t = time.time()
    success, scene = create_scene(executable=None, **vars(args), **extra_args)
    print("Time in seconds to generate map: {}".format(time.time() - t))

    # If we want to show the map and we were successful
    if args.show and success:
        if args.engine is None or args.engine.lower() == "pyvista":
            scene.remove(scene.root.agents_root)

        scene.show()

        input("Press Enter to continue...")
        scene.close()

    if success:
        print("Successful generation!")
    else:
        print("Failed to generate!")
