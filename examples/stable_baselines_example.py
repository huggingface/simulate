import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env


def create_tmaze():
    scene = sm.Scene(engine="Unity")


    scene += sm.Light(
        name="sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
    )
    scene += sm.Cube(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Cube(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Cube(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Cube(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Cube(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Cube(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Cube(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Cube(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Cube(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


    agent = sm.RLAgent(name="agent", turn_speed=5.0,camera_width=36, camera_height=36,  position=[0, 0, 0.0], rotation=utils.quat_from_degrees(0, -180, 0))
    scene += sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)

    reward_function = reward_function = sm.RLAgentRewardFunction(
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
        threshold=3.0,
        is_terminal=True
    )
    agent.add_reward_function(reward_function)
    agent.add_reward_function(reward_function2)
    scene += agent

    return scene


scene = create_tmaze()
scene.show()

env = RLEnv(scene)

obs = env.reset()

#check_env(env)
model = PPO("CnnPolicy", env, verbose=2)
model.learn(total_timesteps=10000)

env.close()