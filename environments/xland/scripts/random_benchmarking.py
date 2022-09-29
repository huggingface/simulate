# Random benchmarking for comparison's purpose with the exploration
# and PPO algorithms

import argparse
import os
import pickle
import time

import numpy as np
from xland.prebuilt import make_prebuilt_env


def sample_n_random(sample_fn, n):
    return np.array([sample_fn() for _ in range(n)])


# TODO: check if seeding works properly and maybe migrate to using rng keys
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        required=True,
        help="Which environment to make: options are `collect_all`, `toy`, `easy`, `medium`, `hard`",
    )

    # Parameters still to be fixed
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_parallel", default=1, type=int, required=False, help="Number of parallel environments")
    parser.add_argument("--n_maps", default=64, type=int, required=False, help="Total number of maps")
    parser.add_argument("--n_show", default=16, type=int, required=False, help="Number of maps to show at once")
    parser.add_argument("--seed", default=10, type=int, required=False, help="Random seed")
    parser.add_argument("--n_episodes", default=25600, type=int, required=False, help="Number of episodes")
    parser.add_argument("--save_folder", default="results", type=str, required=False, help="Where to save results")
    parser.add_argument("--no_headless", dest="headless", action="store_false")
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    # TODO: add back parallel environments once refactor is done
    assert args.n_parallel == 1

    np.random.seed(args.seed)

    env_fn = make_prebuilt_env(
        args.env,
        executable=args.build_exe,
        n_maps=args.n_maps,
        n_show=args.n_show,
        headless=args.headless,
        starting_port=55000,
        n_parallel=args.n_parallel,
    )

    port = 55000
    env = env_fn(port)

    concurrent_envs = args.n_show * args.n_parallel
    dones = np.zeros(concurrent_envs, dtype=bool)
    env.reset()
    t = time.time()
    curr_rewards = np.zeros(concurrent_envs)
    metrics = {
        "rewards_per_slot": np.zeros(concurrent_envs),
        "episodes_per_slot": np.zeros(concurrent_envs),
    }

    print("Started iterating...")
    while np.sum(metrics["episodes_per_slot"]) <= args.n_episodes:
        actions = sample_n_random(env.action_space.sample, concurrent_envs)
        if np.any(dones):
            idxs = np.where(dones)
            metrics["rewards_per_slot"][idxs] += curr_rewards[idxs]
            metrics["episodes_per_slot"][idxs] += 1
            curr_rewards[idxs] = 0

        else:
            _, rewards, dones, _ = env.step(actions)
            curr_rewards += rewards

    total_time = time.time() - t
    print("Executed in {} seconds".format(total_time))

    metrics["total_time"] = total_time
    with open(os.path.join(args.save_folder, "metrics_" + args.env + ".pickle"), "wb") as output_file:
        pickle.dump(metrics, output_file)
