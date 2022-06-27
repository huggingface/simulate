from requests import head
import simenv as sm
from simenv.assets import material
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from simenv.wrappers import ParallelSimEnv

ED_UNITY_BUILD_URL = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
THOM_UNITY_BUILD_URL = "/Users/thomwolf/Documents/GitHub/hf-simenv/integrations/Unity/builds/simenv_unity.x86_64.app/Contents/MacOS/SimEnv"

def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)
    blue_material = sm.Material(base_color=(0, 0, 0.8))
    red_material = sm.Material(base_color=(0.8, 0, 0))
    gray_material = sm.Material(base_color=(0.8, 0.8, 0.8))
    root = sm.Asset(name="root")
    root += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100], material=blue_material)
    root += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1], material=gray_material)
    root += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1], material=gray_material)
    root += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=gray_material)
    root += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=gray_material)
    root += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=gray_material)
    root += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1], material=gray_material)


    agent = sm.RL_Agent(name="agent", turn_speed=5.0,camera_width=36, camera_height=36,  position=[0, 0, 0.0], rotation=utils.quat_from_degrees(0, -180, 0))
    collectable = sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3, material=red_material)


    reward_function = sm.RLAgentRewardFunction(
        function="dense",
        entity1=agent,
        entity2=collectable,
        distance_metric="euclidean"
    )

    reward_function2 = sm.RLAgentRewardFunction(
        function="sparse",
        entity1=agent,
        entity2=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True
    )
    timeout_reward_function = sm.RLAgentRewardFunction(
        function="timeout",
        entity1=agent,
        entity2=agent,
        distance_metric="euclidean",
        threshold=500,
        is_terminal=True,
        scalar=-1.0,
    )
    agent.add_reward_function(reward_function)
    agent.add_reward_function(reward_function2)
    agent.add_reward_function(timeout_reward_function)
    print(agent.camera.width, agent.camera.height)
    root += agent
    root += collectable

    scene += root

    for x in [-10, 0, 11, 22]:
        for z in [0, 11, 22, 33]:
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
    n_parallel = 16
    env_fn = make_env("/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64")

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    obs = env.reset()
    model = PPO("CnnPolicy", env, verbose=3)
    model.learn(total_timesteps=100000)
    
    env.close()
