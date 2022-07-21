import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env


from parallel_envs import make_env


if __name__ == "__main__":
    n_envs = 16
    #
    bench_index = 200  # used to ensure unique ports
    envs = SubprocVecEnv(
        [
            make_env(
                "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64",
                i + bench_index,
                headless=True,
            )
            for i in range(n_envs)
        ]
    )
    obs = envs.reset()

    total_interactions = 1000
    start = time.time()
    for step in range(total_interactions // n_envs):
        action = [envs.action_space.sample() for _ in range(n_envs)]
        obs, reward, done, info = envs.step(action)

    end = time.time() - start
    envs.close()
    interactions_per_second = total_interactions / end
    time.sleep(3)
    print(n_envs, interactions_per_second)
