import argparse
import pickle

import numpy as np


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", default=None, type=str, required=True, help="Metric to read")
    parser.add_argument("--debug", default=False, action="store_true", help="Show or not extra information")
    args = parser.parse_args()

    with open(args.metric, "rb") as input_file:
        metrics = pickle.load(input_file)

    mean_rewards_per_slot = np.sum(metrics["episode_rewards"], axis=1) / metrics["episodes_per_slot"]

    mean_reward = np.mean(metrics["episode_rewards"])
    std_rewards = np.std(metrics["episode_rewards"])

    print("Mean reward: ", mean_reward, "; Standard deviation: ", std_rewards)

    mean_rewards_across_slots = np.mean(metrics["episode_rewards"], axis=0)
    mean_mean_rewards_across_slots = np.mean(mean_rewards_across_slots)
    std_mean_rewards_across_slots = np.std(mean_rewards_across_slots)

    print(
        "Mean reward with same logic as xland exploration: ",
        mean_mean_rewards_across_slots,
        "; Standard deviation: ",
        std_mean_rewards_across_slots,
    )

    if args.debug:
        for key, value in metrics.items():
            print(key, value)
