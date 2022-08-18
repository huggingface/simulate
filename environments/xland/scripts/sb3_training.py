"""Example with training on SB3"""

import argparse

import numpy as np
from stable_baselines3 import PPO
from xland.prebuilt import make_prebuilt_env

from simenv import ParallelSimEnv


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
    parser.add_argument("--headless", default=True, type=bool, required=False, help="Headless mode")
    args = parser.parse_args()

    np.random.seed(args.seed)

    env_fn = make_prebuilt_env(
        args.env, executable=args.build_exe, n_maps=args.n_maps, n_show=args.n_show, headless=args.headless
    )
    env = ParallelSimEnv(env_fn=env_fn, n_parallel=args.n_parallel)
    model = PPO("MultiInputPolicy", env, verbose=3)
    model.learn(total_timesteps=5000000)

    env.close()
