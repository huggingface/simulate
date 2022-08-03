import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


scene = sm.Scene(engine="Unity")
scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)
scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)

material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
for i in range(20):
    scene += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
target = sm.Box(name="cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
scene += target


agent = sm.SimpleRlAgent(name="agent", position=[0.0, 0.0, 0.0])
scene += agent

scene.show(return_nodes=False, return_frames=False)

plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(40, 64, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

for i in range(1000):
    action = {}
    for agent in scene.agents:
        action[agent.name] = random.randrange(0, 3)
    print(action)
    event = scene.step(action=action)

    agent_data = event["agents"]["agent"]
    print(agent_data["done"], agent_data["reward"])
    obs = np.array(agent_data["frames"]["agent_camera"], dtype=np.uint8)
    obs = obs.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
    axim1.set_data(obs)
    fig1.canvas.flush_events()

    # time.sleep(0.1)

scene.close()
