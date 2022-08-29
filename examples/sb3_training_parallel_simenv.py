import argparse

from stable_baselines3 import PPO

import simenv as sm


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

    agent = sm.SimpleActor(name=f"agent_{index}", position=[0.0, 0.0, 0.0])
    root += agent
    root += sm.RewardFunction(entity_a=agent, entity_b=collectable)

    sparse_reward = sm.RewardFunction(
        type="sparse",
        entity_a=agent,
        entity_b=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True,
        is_collectable=True,
    )

    # varying the timeout to test staggered pooling
    timeout = (index % 3) * 50 + 100
    timeout_reward = sm.RewardFunction(
        type="timeout",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        threshold=timeout,
        is_terminal=True,
        scalar=-1.0,
    )
    agent.add_reward_function(sparse_reward)
    agent.add_reward_function(timeout_reward)

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument("--n_maps", default=12, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.RLEnvironment(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    for i in range(1000):
        obs, reward, done, info = env.step()
    """ model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000) """

    env.close()
