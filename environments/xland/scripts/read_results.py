import argparse
import pickle

import numpy as np


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", default=None, type=str, required=True, help="Metric to read")
    parser.add_argument("--confidence", default=0.95, help="Confidence interval for calculating quantiles")
    parser.add_argument("--debug", default=False, action="store_true", help="Show or not extra information")
    args = parser.parse_args()

    with open(args.metric, "rb") as input_file:
        metrics = pickle.load(input_file)

    mean_reward_per_slot = metrics["rewards_per_slot"] / metrics["episodes_per_slot"]
    median_reward_per_slot = metrics["rewards_per_slot"] / metrics["episodes_per_slot"]

    mean_reward = np.mean(mean_reward_per_slot)
    std_rewards = np.std(mean_reward_per_slot)

    median_reward = np.median(median_reward_per_slot)
    median_std_reward = np.std(median_reward_per_slot)
    quantile_left = np.quantile(median_reward_per_slot, q=(1 - args.confidence) / 2)
    quantile_right = np.quantile(median_reward_per_slot, q=(1 + args.confidence) / 2)

    print("Mean reward: ", mean_reward, "; Standard deviation: ", std_rewards)
    print(
        "Median reward: ",
        median_reward,
        "; Standard deviation: ",
        median_std_reward,
        "; Confidence interval: [",
        quantile_left,
        ", ",
        quantile_right,
        "with confidence ",
        args.confidence,
        "]",
    )

    if args.debug:
        for key, value in metrics.items():
            print(key, value)

        print("Mean reward per slot: ", mean_reward_per_slot)
        print("Median reward per slot: ", median_reward_per_slot)
