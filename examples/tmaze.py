import simenv as sm
import simenv.assets.utils as utils
import time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np


scene = sm.Scene(engine="Unity")

scene += sm.Light(
    name="sun", position=[0, 20, 0], intensity=0.9
)
scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


agent = sm.RlAgent(name="agent", position=[0, 0, 0.0])
agent += sm.Camera(
    name="cam1", position=[5, 6.5, -3.75], rotation=utils.quat_from_degrees(45, -45, 0), width=1024, height=1024
)
scene += agent

scene.show()
plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(agent.camera_height, agent.camera_width, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)
env = RLEnv(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) == int:  # discrete are ints, continuous are numpy arrays
        action = [action]
    else:
        action = action.tolist()

    obs, reward, done, info = env.step(action)
    axim1.set_data(obs)
    fig1.canvas.flush_events()

    time.sleep(0.1)


scene.close()
