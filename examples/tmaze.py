import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RL_Env
import matplotlib.pyplot as plt
import numpy as np
scene = sm.Scene(engine="Unity")


scene += sm.DirectionalLight(
    "sun", translation=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
)
scene += sm.Cube("floor", dynamic=False, translation=[0, -0.05, 0], scale=[100, 0.1, 100])
scene += sm.Cube("wall1", dynamic=False, translation=[-1, 0.5, 0], scale=[0.1, 1, 5.1])
scene += sm.Cube("wall2", dynamic=False, translation=[1, 0.5, 0], scale=[0.1, 1, 5.1])
scene += sm.Cube("wall3", dynamic=False, translation=[0, 0.5, 4.5], scale=[5.9, 1, 0.1])
scene += sm.Cube("wall4", dynamic=False, translation=[-2, 0.5, 2.5], scale=[1.9, 1, 0.1])
scene += sm.Cube("wall5", dynamic=False, translation=[2, 0.5, 2.5], scale=[1.9, 1, 0.1])
scene += sm.Cube("wall6", dynamic=False, translation=[-3, 0.5, 3.5], scale=[0.1, 1, 2.1])
scene += sm.Cube("wall7", dynamic=False, translation=[3, 0.5, 3.5], scale=[0.1, 1, 2.1])
scene += sm.Cube("wall8", dynamic=False, translation=[0, 0.5, -2.5], scale=[1.9, 1, 0.1])


agent = sm.RL_Agent("agent", translation=[0, 0, 0.0])
# agent += sm.Camera(
#     "cam1", translation=[5, 6.5, -3.75], rotation=utils.quat_from_degrees(45, -45, 0), width=1024, height=1024
# )
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