import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random
scene = sm.Scene(engine="Unity")


scene += sm.Light(name="sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5)
scene += sm.Cube(name="floor",  position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50])
scene += sm.Cube(name="wall1", position=[-10, 0.0, 0], bounds=[0, 0.1, 0,1, -10, 10])
scene += sm.Cube(name="wall2",  position=[10, 0.5, 0], bounds=[0, 0.1, 0,1, -10, 10])
scene += sm.Cube(name="wall3", position=[0, 0.5, 10], bounds=[-10, 10, 0,1, 0, 0.1])
scene += sm.Cube(name="wall4", position=[0, 0.5, -10], bounds=[-10, 10, 0,1, 0, 0.1])

for i in range(20):
    scene += sm.Cube(name=f"cube{i}", position=[random.uniform(-9,9), 0.5, random.uniform(-9,9)])


agent = sm.RLAgent(name="agent", camera_width=64, camera_height=40, position=[0, 0, 0.0])

reward_function = sm.RLAgentRewardFunction(
    function="dense",
    entity1="agent",
    entity2="cube0",
    distance_metric="euclidean"
)
agent.add_reward_function(reward_function)

scene += agent

scene.show()
plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(agent.camera_height, agent.camera_width, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

env = RLEnv(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) == int: # discrete are ints, continuous are numpy arrays
        action = [action]
    else:
        action = action.tolist()

    obs, done, reward, info = env.step(action)
    print(done, reward, info)
    axim1.set_data(obs)
    fig1.canvas.flush_events()
    
    #time.sleep(0.1)

scene.close()