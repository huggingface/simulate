# Random benchmarking for comparison's purpose with the exploration
# and PPO algorithms

import argparse
import os
import pickle
import time

import numpy as np
from xland.prebuilt import make_prebuilt_env

from simenv import ParallelSimEnv


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
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument("--n_parallel", default=4, type=int, required=False, help="Number of parallel environments")
    parser.add_argument("--n_maps", default=64, type=int, required=False, help="Total number of maps")
    parser.add_argument("--n_show", default=16, type=int, required=False, help="Number of maps to show at once")
    parser.add_argument(
        "--n_parallel_eval", default=2, type=int, required=False, help="Number of parallel environments on eval"
    )
    parser.add_argument("--n_maps_eval", default=16, type=int, required=False, help="Total number of maps on eval")
    parser.add_argument(
        "--n_show_eval", default=8, type=int, required=False, help="Number of maps to show at once on eval"
    )
    parser.add_argument("--seed", default=10, type=int, required=False, help="Random seed")
    parser.add_argument("--n_episodes", default=3200, type=int, required=False, help="Number of episodes")
    parser.add_argument("--save_folder", default="results", type=str, required=False, help="Where to save results")
    parser.add_argument("--env_to_use", default="eval", type=str, required=False, help="Whether to use train or eval")
    parser.add_argument("--headless", default=False, type=bool, required=False, help="Headless mode")
    args = parser.parse_args()

    np.random.seed(args.seed)

    env_fn = make_prebuilt_env(
        args.env,
        executable=args.build_exe,
        n_maps=args.n_maps,
        n_show=args.n_show,
        headless=args.headless,
    )

    train_env = ParallelSimEnv(env_fn=env_fn, n_parallel=args.n_parallel, starting_port=55000)

    eval_env_fn = make_prebuilt_env(
        args.env, executable=args.build_exe, n_maps=args.n_maps_eval, n_show=args.n_show_eval, headless=args.headless
    )

    eval_env = ParallelSimEnv(
        env_fn=eval_env_fn, n_parallel=args.n_parallel_eval, starting_port=55000 + args.n_parallel
    )

    if args.env_to_use == "train":
        env = train_env
        n_show = args.n_show
        n_maps = args.n_maps
        n_parallel = args.n_parallel
    elif args.env_to_use == "eval":
        env = eval_env
        n_show = args.n_show_eval
        n_maps = args.n_maps_eval
        n_parallel = args.n_parallel_eval
    else:
        raise ValueError("env_to_use must be either 'train' or 'eval'")

    concurrent_envs = n_show * n_parallel
    dones = np.zeros(concurrent_envs, dtype=bool)
    env.reset()
    t = time.time()
    curr_rewards = np.zeros(concurrent_envs)
    metrics = {
        "episode_rewards": np.zeros((concurrent_envs, args.n_episodes // concurrent_envs)),
        "episodes_per_slot": np.zeros(concurrent_envs, dtype=int),
    }

    print("Started iterating...")
    current_nb_episodes = 0
    while current_nb_episodes < args.n_episodes:
        actions = sample_n_random(env.action_space.sample, concurrent_envs)
        if np.any(dones):
            idxs = np.where(dones)
            metrics["episode_rewards"][idxs, metrics["episodes_per_slot"][0]] += curr_rewards[idxs]
            metrics["episodes_per_slot"][idxs] += 1

            curr_rewards[idxs] = 0
            current_nb_episodes = np.sum(metrics["episodes_per_slot"])
            dones = np.zeros(concurrent_envs, dtype=bool)

            print("Finished episodes {}".format(current_nb_episodes))

        else:
            _, rewards, dones, _ = env.step(actions)
            curr_rewards += rewards

    env.close()

    total_time = time.time() - t
    print("Executed in {} seconds".format(total_time))

    metrics["total_time"] = total_time
    with open(
        os.path.join(
            args.save_folder, "metrics_" + args.env + "_" + args.env_to_use + "_" + str(args.seed) + ".pickle"
        ),
        "wb",
    ) as output_file:
        pickle.dump(metrics, output_file)
