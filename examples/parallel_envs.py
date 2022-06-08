
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

def create_env(executable=None, port=None):
    scene = sm.Scene(engine="Unity", executable=executable, port=port)


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


    agent = sm.RL_Agent(name="agent", turn_speed=5.0,camera_width=36, camera_height=36,  position=[0, 0, 0.0], rotation=utils.quat_from_degrees(0, -180, 0))
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
    scene.show()

    env = RLEnv(scene)

    return env



if __name__ == "__main__":
    def make_env(executable, rank, seed=0):
        def _make_env():
            print("rank", rank)
            env = create_env(executable=executable, port=55000+rank)
            return env

        return _make_env

    n_envs = 16

    envs = SubprocVecEnv([make_env("/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64", i) for i in range(n_envs)])

    obs = envs.reset()
    # envs.reset()
    # for i in range(1000):
    #     action = [[envs.action_space.sample()] for _ in range(n_envs)]
    #     print(action)
    #     obs, reward, done, info = envs.step(action)
    #     print(done, reward)
    #     #time.sleep(0.1)
    model = PPO("CnnPolicy", envs, verbose=3)
    model.learn(total_timesteps=100000)
    
    envs.close()


    # env = create_env(executable="/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64", port=55000)

    # for i in range(1000):
    #     action = env.action_space.sample()
    #     if type(action) == int: # discrete are ints, continuous are numpy arrays
    #         action = [action]
    #     else:
    #         action = action.tolist()

    #     obs, reward, done, info = env.step(action)
    #     print(done, reward, info)
        
    #     #time.sleep(0.1)

    #     env.close()