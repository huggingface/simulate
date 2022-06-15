import simenv as sm
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random
scene = sm.Scene(engine="Unity")


scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

blue_material = sm.Material(base_color=(0, 0, 0.8))
red_material = sm.Material(base_color=(0.8, 0, 0))
scene += sm.Cube(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=blue_material)
scene += sm.Cube(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
scene += sm.Cube(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
scene += sm.Cube(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)
scene += sm.Cube(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)

for i in range(20):
    material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
    scene += sm.Cube(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)


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
dummy_obs = np.zeros(shape=(agent.camera.height, agent.camera.width, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

env = RLEnv(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) != int:  # discrete are ints, continuous are numpy arrays
        action = action.tolist()        

    obs, reward, done, info = env.step(action)
    print(done, reward, info)
    axim1.set_data(obs.transpose(1,2,0))
    fig1.canvas.flush_events()

    # time.sleep(0.1)

scene.close()
