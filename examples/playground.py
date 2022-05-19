import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RL_Env
import matplotlib.pyplot as plt
import numpy as np
import random
scene = sm.Scene(engine="Unity")


scene += sm.DirectionalLight(
    "sun", translation=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
)
scene += sm.Cube("floor", dynamic=False, translation=[0, -0.05, 0], scale=[100, 0.1, 100])
scene += sm.Cube("wall1", dynamic=False, translation=[-10, 0.5, 0], scale=[0.1, 1, 20.0])
scene += sm.Cube("wall2", dynamic=False, translation=[10, 0.5, 0], scale=[0.1, 1, 20.0])
scene += sm.Cube("wall3", dynamic=False, translation=[0, 0.5, 10], scale=[20.0, 1, 0.1])
scene += sm.Cube("wall4", dynamic=False, translation=[0, 0.5, -10], scale=[20.0, 1, 0.1])

for i in range(20):
    scene += sm.Cube(f"cube{i}", dynamic=False, translation=[random.uniform(-9,9), 0.5, random.uniform(-9,9)], scale=[1,1,1])


agent = sm.RL_Agent("agent", camera_width=64, camera_height=40, translation=[0, 0, 0.0])
scene += agent


scene.build()
plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(agent.camera_height, agent.camera_width, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

env = RL_Env(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) == int: # discrete are ints, continuous are numpy arrays
        action = [action]
    else:
        action = action.tolist()

    obs = env.step(action)
    axim1.set_data(obs)
    fig1.canvas.flush_events()
    
    time.sleep(0.1)


scene.close()