
from requests import head
import simenv as sm
import simenv.assets.utils as utils
import os, time

import matplotlib.pyplot as plt
import numpy as np
import random
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3 import PPO

ED_UNITY_BUILD_URL = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
THOM_UNITY_BUILD_URL = "/Users/thomwolf/Documents/GitHub/hf-simenv/integrations/Unity/builds/simenv_unity.x86_64.app/Contents/MacOS/SimEnv"

def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)


    scene += sm.Light(
        name="sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
    )
    scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


    
    agent = sm.SimpleRlAgent(camera_width=64, camera_height=40, position=[0.0, 0.0, 0.0])
    collectable = sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)
    scene += collectable

    reward_function = sm.RewardFunction(
        type="dense",
        entity_a=agent,
        entity_b=collectable,
        distance_metric="euclidean"
    )

    reward_function2 = sm.RewardFunction(
        type="sparse",
        entity_a=agent,
        entity_b=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True,
        is_collectable=True

    )
    timeout_reward_function = sm.RewardFunction(
        type="timeout",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        threshold=200,
        is_terminal=True,
        scalar=-1.0,
    )
    agent.add_reward_function(reward_function)
    agent.add_reward_function(reward_function2)
    agent.add_reward_function(timeout_reward_function)
    scene += agent
    scene.show()

    return scene

def make_env(executable, rank, seed=0, headless=None):
    def _make_env():
        print("rank", rank)
        env = create_env(executable=executable, port=55000+rank, headless=headless)
        return env

    return _make_env

if __name__ == "__main__":
    n_envs = 1
    # envs = SubprocVecEnv([make_env("/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64", i) for i in range(n_envs)])
    envs = SubprocVecEnv([make_env(None, i) for i in range(n_envs)])
    print(envs.observation_space)

    obs = envs.reset()
    model = PPO("CnnPolicy", envs, verbose=3)
    model.learn(total_timesteps=100000)
    
    envs.close()
