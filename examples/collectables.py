from requests import head
import simenv as sm
from simenv.assets import material
from simenv.assets.agent import rl_agent_actions
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


def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)
    blue_material = sm.Material(base_color=(0, 0, 0.8))
    red_material = sm.Material(base_color=(0.8, 0, 0))
    green_material = sm.Material(base_color=(0.2, 0.8, 0.2))
    gray_material = sm.Material(base_color=(0.8, 0.8, 0.8))
    root = sm.Asset(name="root")
    root += sm.Box(name="floor", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 51], material=blue_material)
    root += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=gray_material)
    root += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=gray_material)
    root += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=gray_material)
    root += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=gray_material)

    agent = sm.RL_Agent(
        name="agent",
        turn_speed=5.0,
        camera_width=36,
        camera_height=36,
        position=[0, 0, 0.0],
        rotation=[0, -180, 0],
        rl_agent_actions=rl_agent_actions.DiscreteRLAgentActions.simple(),
    )
    root += agent
    for i in range(20):

        # material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
        collectable = sm.Sphere(
            name=f"collectable_{i}",
            position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
            radius=0.4,
            material=green_material,
        )

        root += collectable

        reward_function = sm.RLAgentRewardFunction(
            function="sparse",
            entity1=agent,
            entity2=collectable,
            distance_metric="euclidean",
            threshold=1.0,
            is_terminal=False,
            is_collectable=True,
        )
        agent.add_reward_function(reward_function)

    timeout_reward_function = sm.RLAgentRewardFunction(
        function="timeout",
        entity1=agent,
        entity2=agent,
        distance_metric="euclidean",
        threshold=500,
        is_terminal=True,
        scalar=-1.0,
    )

    agent.add_reward_function(timeout_reward_function)

    scene += root

    for x in [0, 21, 42, 63]:
        for z in [0, 21, 42, 63]:
            if x == 0 and z == 0:
                continue
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

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel, starting_port=56000)

    obs = env.reset()
    model = PPO("CnnPolicy", env, verbose=3, n_steps=200, n_epochs=2, batch_size=1280)
    model.learn(total_timesteps=1000000)

    env.close()
