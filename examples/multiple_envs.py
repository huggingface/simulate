import time
import simenv as sm
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np
import random


scene = sm.Scene(engine="unity")
scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

root = sm.Asset(name="root")
blue_material = sm.Material(base_color=(0, 0, 0.8))
red_material = sm.Material(base_color=(0.8, 0, 0))
root += sm.Box(name="floor", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 51], material=blue_material)
root += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
root += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=red_material)
root += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)
root += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=red_material)


material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
cube = sm.Box(name=f"cube0", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
root += cube
for i in range(20):
    material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
    root += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

agent = sm.RlAgent(name="agent", camera_width=64, camera_height=40, position=[0, 0, 0.0])
reward_function = sm.RlAgentRewardFunction(
    function="dense",
    entity_a=agent,
    entity_b=cube,
    distance_metric="euclidean",

)
agent.add_reward_function(reward_function)

root += agent
scene += root

for x in [0, 21, 42, 63]:
    for z in [0, 21, 42, 63]:
        if x ==0 and z == 0: continue
        scene += root.copy().translate_x(x).translate_z(z)

print(scene)
print(agent.camera.height, agent.camera.width)
#exit()
scene.show()
env = RLEnv(scene)

plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(agent.camera.height*4, agent.camera.width*4, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)



for i in range(1000):
    actions = [env.action_space.sample() for _ in range(env.n_agents)]
    # if type(action) != int:  # discrete are ints, continuous are numpy arrays
    #     action = action.tolist()        

    obs, reward, done, info = env.step(actions)

    # for i in range(4):
    #     for j in range(4):
    #         dummy_obs[i*agent.camera.height:(i+1)*agent.camera.height,j*agent.camera.width:(j+1)*agent.camera.width] = obs[i*4+j].transpose(1,2,0)
    # axim1.set_data(dummy_obs)
    # fig1.canvas.flush_events()
    print(done, reward, info)

    # time.sleep(0.1)

scene.close()