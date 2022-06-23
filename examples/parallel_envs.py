
from requests import head
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

def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", executable=executable, port=port, headless=headless)


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


    agent = sm.RlAgent(name="agent", turn_speed=5.0,camera_width=36, camera_height=36,  position=[0, 0, 0.0], rotation=utils.quat_from_degrees(0, -180, 0))
    scene += sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)

    reward_function = sm.RLAgentRewardFunction(
        function="dense",
        entity1="agent",
        entity2="collectable",
        distance_metric="euclidean"
    )

    reward_function2 = sm.RLAgentRewardFunction(
        function="sparse",
        entity1="agent",
        entity2="collectable",
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True
    )
    timeout_reward_function = sm.RLAgentRewardFunction(
        function="timeout",
        entity1="agent",
        entity2="agent",
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

    env = RLEnv(scene)

    return env

def make_env(executable, rank, seed=0, headless=None):
    def _make_env():
        print("rank", rank)
        env = create_env(executable=executable, port=55000+rank, headless=headless)
        return env

    return _make_env

if __name__ == "__main__":


    n_envs = 16

    # envs = SubprocVecEnv([make_env("/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64", i) for i in range(n_envs)])
    envs = SubprocVecEnv([make_env("integrations/Unity/Build/SimEnv.exe", i) for i in range(n_envs)])

    obs = envs.reset()
    model = PPO("CnnPolicy", envs, verbose=3)
    model.learn(total_timesteps=100000)
    
    envs.close()
