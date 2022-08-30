import argparse
import time

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64


def create_scene(port=55000):
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    scene = sm.Scene(engine="Unity", engine_exe=args.build_exe, frame_skip=4, engine_port=port)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
    scene += sm.Box(name="wall1", position=[-5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    scene += sm.Box(name="wall2", position=[5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    scene += sm.Box(name="wall3", position=[0, 0, 5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    scene += sm.Box(name="wall4", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    scene += sm.Box(name="target", position=[1, 0.5, 1], material=sm.Material.RED)
    scene += sm.Box(name="target_2", position=[-1, 0.5, 1], material=sm.Material.GREEN)
    scene += sm.SimpleActor(
        name="agent",
        camera_width=CAMERA_WIDTH,
        camera_height=CAMERA_HEIGHT,
        position=[0.0, 0.1, 0.0],
    )

    return scene


def run_scene(scene):
    scene.show()
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    scene.reset()
    for i in range(50):
        action = scene.action_space.sample()
        obs, reward, done, info = scene.step(action)

        print(done, reward, info)
        axim1.set_data(obs["CameraSensor"].transpose(1, 2, 0))
        fig1.canvas.flush_events()

        time.sleep(0.1)

    scene.close()
    plt.close()


scene = create_scene()

target_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

not_reward = sm.RewardFunction(
    type="not",
    entity_a=scene.agent,
    entity_b=scene.agent,
    distance_metric="euclidean",
    reward_function_a=target_reward,
    is_terminal=True,
)
scene.agent.add_reward_function(not_reward)
run_scene(scene)

# Second iteration:
scene = create_scene(port=55001)
target_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

target_2_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target_2,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

and_reward = sm.RewardFunction(
    type="and",
    entity_a=scene.agent,
    entity_b=scene.agent,
    distance_metric="euclidean",
    reward_function_a=target_reward,
    reward_function_b=target_2_reward,
)

scene.agent.add_reward_function(and_reward)
run_scene(scene)

# Third iteration:
scene = create_scene(port=55002)
target_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

target_2_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target_2,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

or_reward = sm.RewardFunction(
    type="or",
    entity_a=scene.agent,
    entity_b=scene.agent,
    distance_metric="euclidean",
    reward_function_a=target_reward,
    reward_function_b=target_2_reward,
)

scene.agent.add_reward_function(or_reward)
run_scene(scene)

# Fourth iteration:
scene = create_scene(port=55003)
target_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

target_2_reward = sm.RewardFunction(
    type="sparse",
    entity_a=scene.agent,
    entity_b=scene.target_2,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=1.0,
    trigger_once=False,
)

xor_reward = sm.RewardFunction(
    type="xor",
    entity_a=scene.agent,
    entity_b=scene.agent,
    distance_metric="euclidean",
    reward_function_a=target_reward,
    reward_function_b=target_2_reward,
)

scene.agent.add_reward_function(xor_reward)
run_scene(scene)
