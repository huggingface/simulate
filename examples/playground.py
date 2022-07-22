import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


scene = sm.Scene(engine="Unity")
scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

blue_material = sm.Material(base_color=(0, 0, 0.8))
red_material = sm.Material(base_color=(0.8, 0, 0))

scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=blue_material)
scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)
scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)

material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
for i in range(20):
    scene += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
target = sm.Box(name=f"cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
scene += target

agent = sm.SimpleRlAgent(camera_width=64, camera_height=40, reward_target=target, position=[0, 0, 0.0])
scene += agent

agent.observation_space

scene.show()
plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(*agent.observation_space.shape[1:], agent.observation_space.shape[0]), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

scene.reset()
for i in range(1000):
    action = scene.action_space.sample()
    print(action)
    obs, reward, done, info = scene.step(action)

    print(done, reward, info)
    axim1.set_data(obs.transpose(1, 2, 0))
    fig1.canvas.flush_events()

    # time.sleep(0.1)

scene.close()
