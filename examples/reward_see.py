import random
import time

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"


def create_scene(port=55000):
    scene = sm.Scene(engine="Unity", engine_exe=None, frame_skip=4, engine_port=port)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    blue_material = sm.Material.BLUE
    red_material = sm.Material.RED
    yellow_material = sm.Material.YELLOW
    green_material = sm.Material.GREEN

    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=blue_material)
    scene += sm.Box(name="wall1", position=[-5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=red_material)
    scene += sm.Box(name="wall2", position=[5, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=red_material)
    scene += sm.Box(name="wall3", position=[0, 0, 5], bounds=[-5, 5, 0, 1, 0, 0.1], material=red_material)
    scene += sm.Box(name="wall4", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=red_material)
    scene += sm.Box(name="target", position=[1, 0.5, 1], material=red_material)
    scene += sm.SimpleRlAgent(name="agent", camera_width=64, camera_height=40, position=[0, 0.1, 0.0])

    return scene


def run_scene(scene, fixed_action=None):
    scene.show()
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(
        shape=(*scene.agent.observation_space.shape[1:], scene.agent.observation_space.shape[0]), dtype=np.uint8
    )
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    scene.reset()
    for i in range(50):
        if fixed_action is None:
            action = scene.action_space.sample()
        else:
            action = fixed_action
        obs, reward, done, info = scene.step(action)

        print(done, reward, info)
        axim1.set_data(obs.transpose(1, 2, 0))
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
    trigger_once=False,
)

scene.agent.add_reward_function(target_reward)
run_scene(scene, fixed_action=1)
