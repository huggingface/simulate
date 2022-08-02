"""Example with training on SB3"""

import argparse

import numpy as np
from stable_baselines3 import PPO
from xland import make_env

from simenv import ParallelSimEnv


# TODO: check if seeding works properly and maybe migrate to using rng keys
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    n_parallel = 4
    seed = 10
    np.random.seed(seed)

    example_map = np.load("benchmark/examples/example_map_01.npy")
    env_fn = make_env(
        executable=args.build_exe,
        headless=True,
        sample_from=example_map,
        engine="Unity",
        seed=None,
        n_agents=1,
        n_objects=6,
        width=6,
        height=6,
        n_show=9,
        n_maps=250,
    )

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    model = PPO("MultiInputPolicy", env, verbose=3)
    model.learn(total_timesteps=5000000)

    env.close()
