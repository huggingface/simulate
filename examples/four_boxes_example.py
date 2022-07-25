import simenv as sm
import matplotlib.pyplot as plt
import numpy as np
import random
import time


ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"

def create_scene(port=55000):
    scene = sm.Scene(engine="Unity", engine_exe=ALICIA_UNITY_BUILD_URL, frame_skip=10, engine_port=port)
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

    blue_material = sm.Material.BLUE
    red_material = sm.Material.RED
    yellow_material = sm.Material.YELLOW
    green_material = sm.Material.GREEN
    white_material = sm.Material.WHITE

    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=blue_material)
    scene += sm.Box(name="wall1", position=[-5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=red_material)
    scene += sm.Box(name="wall2", position=[5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=red_material)
    scene += sm.Box(name="wall3", position=[0, 0, 5], bounds=[-5, 5, 0, 1, 0, 0.1], material=red_material)
    scene += sm.Box(name="wall4", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=red_material)
    mass = 0.2
    scene += sm.Box(name="red_target", position=[-2, 0.5, 2], material=red_material, physics_component=sm.RigidBody(mass=mass))
    scene += sm.Box(name="yellow_target", position=[-2, 0.5, -2], material=yellow_material, physics_component=sm.RigidBody(mass=mass))
    scene += sm.Box(name="green_target", position=[2, 0.5, -2], material=green_material, physics_component=sm.RigidBody(mass=mass))
    scene += sm.Box(name="white_target", position=[2, 0.5, 2], material=white_material, physics_component=sm.RigidBody(mass=mass))
    scene += sm.SimpleRlAgent(name="agent", camera_width=64, camera_height=40, position=[0, 0, 0.0])
    
    return scene

def run_scene(scene):
    scene.show()
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(*scene.agent.observation_space.shape[1:], scene.agent.observation_space.shape[0]), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    scene.reset()
    for i in range(1000):
        action = scene.action_space.sample()
        obs, reward, done, info = scene.step(action)

        print(done, reward, info)
        axim1.set_data(obs.transpose(1, 2, 0))
        fig1.canvas.flush_events()

        time.sleep(0.1)

    scene.close()
    plt.close()

scene = create_scene()

red_yellow_target_reward_single = sm.RewardFunction(
    type="sparse",
    entity_a=scene.red_target,
    entity_b=scene.yellow_target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=10.0,
    trigger_once=True,
)

red_yellow_target_reward_multiple = sm.RewardFunction(
    type="sparse",
    entity_a=scene.red_target,
    entity_b=scene.yellow_target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=20.0,
    trigger_once=False,
)

green_white_target_reward_single = sm.RewardFunction(
    type="sparse",
    entity_a=scene.green_target,
    entity_b=scene.white_target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=10.0,
    trigger_once=True,
)

green_white_target_reward_multiple = sm.RewardFunction(
    type="sparse",
    entity_a=scene.red_target,
    entity_b=scene.yellow_target,
    distance_metric="euclidean",
    threshold=2.0,
    is_terminal=False,
    is_collectable=False,
    scalar=20.0,
    trigger_once=False,
)

and_reward = sm.RewardFunction(
    type="and",
    entity_a=scene.agent,
    entity_b=scene.agent,
    distance_metric="euclidean",
    reward_function_a=red_yellow_target_reward_multiple,
    reward_function_b=green_white_target_reward_multiple,
    is_terminal=True,
)

scene.agent.add_reward_function(red_yellow_target_reward_single)
scene.agent.add_reward_function(green_white_target_reward_single)
scene.agent.add_reward_function(and_reward)
run_scene(scene)