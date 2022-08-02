import time
import argparse
import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64


def create_scene(port=55000):
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    scene = sm.Scene(engine="Unity", engine_exe=args.build_exe, frame_skip=10, engine_port=port)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
    scene += sm.Box(name="wall1", position=[-5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    scene += sm.Box(name="wall2", position=[5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.RED)
    scene += sm.Box(name="wall3", position=[0, 0, 5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    scene += sm.Box(name="wall4", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.RED)
    mass = 0.2
    scene += sm.Box(
        name="target",
        position=[-2, 0.5, 2],
        material=sm.Material.RED,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    scene += sm.SimpleRlAgent(
        name="agent",
        sensors=[
            sm.CameraSensor(width=CAMERA_WIDTH, height=CAMERA_HEIGHT, position=[0, 0.1, 0]),
        ],
        position=[0.0, 0.0, 0.0],
    )

    return scene


def run_scene(scene, fixed_action=None):
    scene.show()
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    scene.reset()
    for i in range(50):
        if fixed_action is None:
            action = scene.action_space.sample()
        else:
            action = fixed_action
        obs, reward, done, info = scene.step(action)

        print(done, reward, info)
        axim1.set_data(obs["CameraSensor"].transpose(1, 2, 0))
        fig1.canvas.flush_events()

        time.sleep(0.1)

    scene.close()
    plt.close()


scene = create_scene()

target_reward = sm.RewardFunction(
    type="see",
    entity_a=scene.agent,
    entity_b=scene.target,
    distance_metric="euclidean",
    threshold=30.0,
    is_terminal=False,
    is_collectable=True,
    scalar=1.0,
    trigger_once=True,
)

scene.agent.add_reward_function(target_reward)
run_scene(scene, fixed_action=1)
