import simenv as sm
import simenv.assets.utils as utils
from simenv.assets import material
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random
scene = sm.Scene(engine="Unity")


mat_purple = material.Material(name="purple", base_color=[0.3,0.3,0.4], metallic_factor=1.0, roughness_factor=0.0)
mat_dark = material.Material(name="gray", base_color=[0.1,0.1,0.1], metallic_factor=1.0, roughness_factor=0.0)
mat_red = material.Material(name="red", base_color=[0.8,0.2,0.2], metallic_factor=1.0, roughness_factor=0.0)
mat_white = material.Material(name="white", base_color=[0.8,0.8,0.8], metallic_factor=1.0, roughness_factor=0.0)

scene += sm.Light(name="sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(-60, -30, 0), intensity=2.0)
scene += sm.Cube(name="floor", material=mat_dark,  position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50])
scene += sm.Cube(name="wall1", material=mat_purple, position=[-6, 0.0, 0], bounds=[0, 0.1, 0, 1, -6, 6])
scene += sm.Cube(name="wall2", material=mat_purple,  position=[6, 0.0, 0], bounds=[0, 0.1, 0,1, -6, 6])
scene += sm.Cube(name="wall3", material=mat_purple, position=[0, 0.0, 6], bounds=[-6, 6, 0,1, 0, 0.1])
scene += sm.Cube(name="wall4", material=mat_purple, position=[0, 0.0, -6], bounds=[-6, 6, 0,1, 0, 0.1])


positions_cube = [
    [-2,.5,2],
    [2,.5,2],

]

for i, position in enumerate(positions_cube):
    scene += sm.Cube(name=f"cube{i}",material=mat_red, position=position)

position_sphere = [
    [-3.0,.5,-2.5],
    [-2.25,.5,-3.4],
    [-1.17,.5,-3.9],
    [0,.5,-4],
    [1.17,.5,-3.9],
    [2.25,.5,-3.4],
    [3.0,.5,-2.5],
]
for i, position in enumerate(position_sphere):
    scene += sm.Sphere(name=f"sphere{i}", material=mat_white, position=position, radius=0.5)

agent = sm.RL_Agent(name="agent", camera_width=64, camera_height=40, position=[0, 0, 0.0])

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