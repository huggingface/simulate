import os
import random
import time

import matplotlib.pyplot as plt
import numpy as np
from requests import head
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import SubprocVecEnv

import simenv as sm
import simenv.assets.utils as utils
from simenv import ParallelSimEnv
from simenv.assets import material


ED_UNITY_BUILD_URL = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
THOM_UNITY_BUILD_URL = "/Users/thomwolf/Documents/GitHub/hf-simenv/integrations/Unity/builds/simenv_unity.x86_64.app/Contents/MacOS/SimEnv"
ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"


def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(
        engine="Unity",
        engine_exe=executable,
        engine_port=port,
        engine_headless=headless,
        frame_skip=4,
        physics_update_rate=30,
    )
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
    blue_material = sm.Material(base_color=(0, 0, 0.8))
    red_material = sm.Material(base_color=(0.8, 0, 0))
    gray_material = sm.Material(base_color=(0.8, 0.8, 0.8))
    root = sm.Asset(name="root")
    root += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[10, 0.1, 10], material=blue_material)
    root += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1], material=gray_material)
    root += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1], material=gray_material)
    root += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=gray_material)
    root += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=gray_material)
    root += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1], material=gray_material)

    agent = sm.SimpleRlAgent(
        sensors=[
            sm.CameraSensor(width=64, height=40, position=[0, 0.75, 0]),
        ],
        position=[0.0, 0.0, 0.0],
    )
    collectable = sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)
    scene += collectable

    reward_function = sm.RewardFunction(
        type="dense", entity_a=agent, entity_b=collectable, distance_metric="euclidean"
    )

    reward_function2 = sm.RewardFunction(
        type="sparse",
        entity_a=agent,
        entity_b=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True,
        is_collectable=True,
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
    root += agent
    root += collectable
    scene.engine.add_to_pool(root)
    for i in range(15):
        scene.engine.add_to_pool(root.copy())

    scene.show(n_maps=16)

    return scene


def make_env(executable, seed=0, headless=True):
    def _make_env(port):
        env = create_env(executable=executable, port=port, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = 1
    env_fn = make_env(None)  # "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64")  #

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    # obs = env.reset()

    # for i in range(100):
    #     actions = np.array([env.action_space.sample() for _ in range(env.n_agents)])
    #     print(i)
    #     obs = env.step(actions)

    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
