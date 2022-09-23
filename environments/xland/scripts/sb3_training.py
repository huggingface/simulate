"""Example with training on SB3"""

import argparse

import numpy as np
from xland.prebuilt import make_prebuilt_env

from simulate import logging


logger = logging.get_logger(__name__)

try:
    from stable_baselines3 import PPO
except ImportError:
    logger.warning(
        "stable-baseline3 is required for this example and is not installed. To install: pip install simulate[sb3]"
    )
    exit()


# TODO: check if seeding works properly and maybe migrate to using rng keys
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        required=True,
        help="Which environment to make: options are `collect_all`, `toy`, `easy`, `medium`, `hard`",
    )
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_parallel", default=2, type=int, required=False, help="Number of parallel environments")
    parser.add_argument("--n_maps", default=16, type=int, required=False, help="Total number of maps")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show at once")
    parser.add_argument("--seed", default=10, type=int, required=False, help="Random seed")
    parser.add_argument("--headless", default=True, type=bool, required=False, help="Headless mode")
    args = parser.parse_args()

    np.random.seed(args.seed)
    env_fn = make_prebuilt_env(
        args.env,
        executable=args.build_exe,
        n_maps=args.n_maps,
        n_show=args.n_show,
        headless=args.headless,
    )

    port = 55000
    # TODO: add back parallel environments once refactor is done
    model = PPO("MultiInputPolicy", env_fn(port), verbose=3)
    model.learn(total_timesteps=5000000)
