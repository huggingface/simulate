import argparse

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv

import simenv as sm


def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)

    scene += sm.Light(name="sun", position=[0, 20, 0], rotation=[60, -30, 0], intensity=3.5)
    scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])

    collectable = sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)
    scene += collectable

    agent = sm.EgocentricCameraAgent(position=[0, 0, 0], reward_target=collectable)
    scene += agent

    sparse_reward = sm.RewardFunction(
        type="sparse",
        entity_a=agent,
        entity_b=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True,
        is_collectable=True,
    )
    timeout_reward = sm.RewardFunction(
        type="timeout",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        threshold=200,
        is_terminal=True,
        scalar=-1.0,
    )
    agent.add_reward_function(sparse_reward)
    agent.add_reward_function(timeout_reward)

    return sm.RLEnvironment(scene)


def make_env(executable, rank, seed=0, headless=None):
    def _make_env():
        print("rank", rank)
        env = create_env(executable=executable, port=55000 + rank, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=True, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    n_envs = 1
    envs = SubprocVecEnv([make_env(args.build_exe, i) for i in range(n_envs)])

    obs = envs.reset()
    model = PPO("MultiInputPolicy", envs, verbose=3)
    model.learn(total_timesteps=100000)

    envs.close()
