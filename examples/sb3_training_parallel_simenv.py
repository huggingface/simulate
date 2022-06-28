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
from simenv import ParallelSimEnv

ED_UNITY_BUILD_URL = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
THOM_UNITY_BUILD_URL = "/Users/thomwolf/Documents/GitHub/hf-simenv/integrations/Unity/builds/simenv_unity.x86_64.app/Contents/MacOS/SimEnv"

def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

    root = sm.Asset(name="root")
    blue_material = sm.Material(base_color=(0, 0, 0.8))
    red_material = sm.Material(base_color=(0.8, 0, 0))
    root += sm.Box(name="floor", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 51], material=blue_material)
    root += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
    root += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
    root += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)
    root += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)


    material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
    cube = sm.Box(name=f"cube0", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
    root += cube
    for i in range(20):
        material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
        root += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

    agent = sm.RlAgent(name="agent", camera_width=64, camera_height=40, position=[0, 0, 0.0])
    reward_function = sm.RlAgentRewardFunction(
        function="dense",
        entity_a=agent,
        entity2=cube,
        distance_metric="euclidean",

    )
    agent.add_reward_function(reward_function)

    root += agent
    scene += root

    for x in [0, 21, 42, 63]:
        for z in [0, 21, 42, 63]:
            if x ==0 and z == 0: continue
            scene += root.copy().translate_x(x).translate_z(z)

    scene.show()
    env = RLEnv(scene)

    return env

def make_env(executable, seed=0, headless=None):
    def _make_env(port):
        env = create_env(executable=executable, port=port, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = 4
    env_fn = make_env(THOM_UNITY_BUILD_URL)

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    obs = env.reset()
    model = PPO("CnnPolicy", env, verbose=3)
    model.learn(total_timesteps=100000)
    
    env.close()
