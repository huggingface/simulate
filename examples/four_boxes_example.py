import argparse
import random

from stable_baselines3 import PPO

import simenv as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")

    root += sm.Box(name=f"floor_{index}", position=[0, 0, 0], bounds=[-5, 5, 0, 0.1, -5, 5], material=sm.Material.BLUE)
    root += sm.Box(name=f"wall1_{index}", position=[-5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    root += sm.Box(name=f"wall2_{index}", position=[5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    root += sm.Box(name=f"wall3_{index}", position=[0, 0, 5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    root += sm.Box(name=f"wall4_{index}", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    mass = 0.2

    red_target = sm.Box(
        name=f"red_target_{index}",
        position=[-2, 0.5, 2],
        material=sm.Material.RED,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    root += red_target

    yellow_target = sm.Box(
        name=f"yellow_target_{index}",
        position=[-2, 0.5, -2],
        material=sm.Material.YELLOW,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    root += yellow_target

    green_target = sm.Box(
        name=f"green_target_{index}",
        position=[2, 0.5, -2],
        material=sm.Material.GREEN,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    root += green_target

    white_target = sm.Box(
        name=f"white_target_{index}",
        position=[2, 0.5, 2],
        material=sm.Material.WHITE,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    root += white_target

    actor = sm.EgocentricCameraActor(
        name=f"actor_{index}",
        camera_height=CAMERA_HEIGHT,
        camera_width=CAMERA_WIDTH,
        position=[0.0, 0.5, 0.0],
    )
    root += actor
    red_yellow_target_reward_single = sm.RewardFunction(
        type="sparse",
        entity_a=red_target,
        entity_b=yellow_target,
        distance_metric="euclidean",
        threshold=2.0,
        is_terminal=False,
        is_collectable=False,
        scalar=10.0,
        trigger_once=True,
    )

    red_yellow_target_reward_multiple = sm.RewardFunction(
        type="sparse",
        entity_a=red_target,
        entity_b=yellow_target,
        distance_metric="euclidean",
        threshold=2.0,
        is_terminal=False,
        is_collectable=False,
        scalar=20.0,
        trigger_once=False,
    )

    green_white_target_reward_single = sm.RewardFunction(
        type="sparse",
        entity_a=green_target,
        entity_b=white_target,
        distance_metric="euclidean",
        threshold=2.0,
        is_terminal=False,
        is_collectable=False,
        scalar=10.0,
        trigger_once=True,
    )

    green_white_target_reward_multiple = sm.RewardFunction(
        type="sparse",
        entity_a=red_target,
        entity_b=yellow_target,
        distance_metric="euclidean",
        threshold=2.0,
        is_terminal=False,
        is_collectable=False,
        scalar=20.0,
        trigger_once=False,
    )

    and_reward = sm.RewardFunction(
        type="and",
        distance_metric="euclidean",
        is_terminal=True,
    )
    and_reward += green_white_target_reward_multiple
    and_reward += red_yellow_target_reward_multiple

    actor += red_yellow_target_reward_single
    actor += green_white_target_reward_single
    actor += and_reward

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument("--n_maps", default=20, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=16, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.RLEnvironment(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    # for i in range(1000):
    #     obs, reward, done, info = env.step()
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
