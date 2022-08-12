"""Example with training on SB3"""

import argparse

import numpy as np
from stable_baselines3 import PPO
from xland.prebuilt import (
    make_collect_all_environment,
    make_easy_environment,
    make_hard_environment,
    make_medium_environment,
    make_toy_environment,
)

from simenv import ParallelSimEnv


NAME_TO_MAKE_ENV = {
    "collect_all": make_collect_all_environment,
    "toy": make_toy_environment,
    "easy": make_easy_environment,
    "medium": make_medium_environment,
    "hard": make_hard_environment,
}

# TODO: check if seeding works properly and maybe migrate to using rng keys
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        required=True,
        help="Which environment to make: options are `collect_all`, `toy`, `easy`, `medium`, `hard`",
    )
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument("--n_parallel", default=4, type=int, required=False, help="Number of parallel environments")
    parser.add_argument("--n_maps", default=16, type=int, required=False, help="Total number of maps")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show at once")
    parser.add_argument("--seed", default=10, type=int, required=False, help="Random seed")
    args = parser.parse_args()

    np.random.seed(args.seed)

    env_fn = NAME_TO_MAKE_ENV[args.env](executable=args.build_exe, n_maps=args.n_maps, n_show=args.n_show)
    env = ParallelSimEnv(env_fn=env_fn, n_parallel=args.n_parallel)
    model = PPO("MultiInputPolicy", env, verbose=3, device="cpu")
    model.learn(total_timesteps=5000000)

    env.close()
