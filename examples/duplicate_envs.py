import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64
SIZE = 4


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")
    root += sm.Box(
        name=f"floor_{index}", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 11], material=sm.Material.BLUE
    )
    root += sm.Box(
        name=f"wall1_{index}", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED
    )
    root += sm.Box(
        name=f"wall2_{index}", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED
    )
    root += sm.Box(
        name=f"wall3_{index}", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED
    )
    root += sm.Box(
        name=f"wall4_{index}", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED
    )

    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    cube = sm.Box(
        name=f"reward_{index}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material
    )
    root += cube
    for i in range(20):
        material = sm.Material(
            base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]
        )
        root += sm.Box(
            name=f"cube{i}_{index}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material
        )

    agent = sm.SimpleRlAgent(name=f"agent_{index}", reward_target=cube, position=[0.0, 0.0, 0.0])

    root += agent
    return root


scene = sm.Scene(engine="unity")
scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
for y in range(SIZE):
    for x in range(SIZE):
        root = generate_map(y * SIZE + x)
        root.position += [y * 20, 0, x * 20]
        scene += root

scene.show(return_cameras=False, return_nodes=False)

plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(CAMERA_HEIGHT * SIZE, CAMERA_WIDTH * SIZE, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

for y in range(1000):
    action = {agent.name: random.randrange(0, 3) for agent in scene.agents}

    event = scene.step(action=action)
    for y in range(SIZE):
        for x in range(SIZE):
            index = y * SIZE + x
            agent_data = event["agents"][f"agent_{index}"]
            print(agent_data["done"], agent_data["reward"])
            obs = np.array(agent_data["frames"][f"agent_{index}_camera"], dtype=np.uint8).transpose((1, 2, 0))
            dummy_obs[y * CAMERA_HEIGHT : (y + 1) * CAMERA_HEIGHT, x * CAMERA_WIDTH : (x + 1) * CAMERA_WIDTH, :] = obs
    axim1.set_data(dummy_obs)
    fig1.canvas.flush_events()

    plt.pause(0.1)

scene.close()
