from stable_baselines3 import PPO

import simenv as sm
from simenv import ParallelRLEnvironment


SIZE = 1

ED_UNITY_BUILD_URL = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
THOM_UNITY_BUILD_URL = "/Users/thomwolf/Documents/GitHub/hf-simenv/integrations/Unity/builds/simenv_unity.x86_64.app/Contents/MacOS/SimEnv"
ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")
    root += sm.Box(name=f"floor_{index}", position=[0, -0.05, 0], scaling=[10, 0.1, 10], material=sm.Material.BLUE)
    root += sm.Box(name=f"wall1_{index}", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall2_{index}", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall3_{index}", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall4_{index}", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall5_{index}", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall6_{index}", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall7_{index}", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1], material=sm.Material.GRAY75)
    root += sm.Box(name=f"wall8_{index}", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1], material=sm.Material.GRAY75)

    collectable = sm.Sphere(name=f"collectable_{index}", position=[2, 0.5, 3.4], radius=0.3)
    root += collectable

    agent = sm.SimpleRlAgent(name=f"agent_{index}", reward_target=collectable, position=[0.0, 0.0, 0.0])
    root += agent

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

    return root


def create_env():
    scene = sm.Scene(engine="Unity")
    scene += sm.LightSun()
    for y in range(SIZE):
        for x in range(SIZE):
            index = y * SIZE + x
            root = generate_map(index)
            root.position += [x * 20, 0, y * 20]
    return scene


def make_env():
    def _make_env(port):
        env = create_env()
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = SIZE * SIZE
    env_fn = make_env()
    env = ParallelRLEnvironment(env_fn=env_fn, n_parallel=n_parallel)
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
