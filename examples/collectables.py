import argparse
import random

from stable_baselines3 import PPO

import simenv as sm


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")
    root += sm.Box(
        name=f"floor_{index}",
        position=[0, 0, 0],
        bounds=[-10, 10, 0, 0.1, -10, 10],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall1_{index}",
        position=[-10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall2_{index}",
        position=[10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall3_{index}",
        position=[0, 0, 10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall4_{index}",
        position=[0, 0, -10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )

    actor = sm.EgocentricCameraActor(position=[0.0, 0.5, 0.0], camera_width=64, camera_height=40)
    root += actor
    for i in range(20):

        # material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
        collectable = sm.Sphere(
            name=f"collectable_{index}_{i}",
            position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
            radius=0.4,
            material=sm.Material.GREEN,
        )

        root += collectable

        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=actor,
            entity_b=collectable,
            distance_metric="euclidean",
            threshold=1.0,
            is_terminal=False,
            is_collectable=True,
        )
        actor += reward_function

    actor += sm.RewardFunction(
        type="timeout",
        entity_a=actor,
        entity_b=actor,
        distance_metric="euclidean",
        threshold=500,
        is_terminal=True,
        scalar=-1.0,
    )

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument("--n_maps", default=12, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.RLEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    # for i in range(1000):
    #     obs, reward, done, info = env.step()
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
