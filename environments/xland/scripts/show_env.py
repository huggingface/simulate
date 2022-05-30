"""
Minimal script for generating a map, and then randomly sampling from it.
"""

import argparse

from xland import gen_setup, generate_env
from xland.utils import create_2d_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--periodic_output", type=bool, default=True)
    parser.add_argument("--periodic_input", type=bool, default=True)
    parser.add_argument("--ground", type=bool, default=False)
    parser.add_argument("--show", type=bool, default=True)

    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max_height", type=int, default=8)
    parser.add_argument("--symmetry", type=int, default=1)
    parser.add_argument("--N", type=int, default=2)
    parser.add_argument("--nb_samples", type=int, default=1)

    parser.add_argument("--sample_from", type=str, default=None)
    parser.add_argument("--specific_map", type=str, default=None)
    parser.add_argument("--folder_path", type=str, default=".gen_files")

    args = parser.parse_args()

    if args.sample_from is None and args.specific_map is None:
        gen_setup(args.max_height)

    else:
        name = args.specific_map or args.sample_from
        map_2d = create_2d_map(name, map_format="rgb")

    _ = generate_env(**vars(args))
