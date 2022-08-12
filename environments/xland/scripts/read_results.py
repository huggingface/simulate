import pickle
import numpy as np
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", default=None, type=str, required=True, help="Metric to read")
    parser.add_argument("--debug", default=False, action='store_true', help="Show or not extra information")
    args = parser.parse_args()

    with open(args.metric, "rb") as input_file:
        metrics = pickle.load(input_file)

    mean_rewards_per_slot = metrics["episode_rewards"] / metrics["episodes_per_slot"]
    mean_reward = np.mean(mean_rewards_per_slot)
    std_rewards = np.std(mean_rewards_per_slot)


    print("Mean reward: ", mean_reward, "; Standard deviation: ", std_rewards)

    if args.debug:
        for key, value in metrics.items():
            print(key, value)