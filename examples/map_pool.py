import simenv as sm
import simenv.assets.utils as utils
import time
import matplotlib.pyplot as plt
import numpy as np

from simenv.rl import agents


scene = sm.Scene(engine="Unity")

# scene += sm.Light(
#     name="sun", position=[0, 20, 0], intensity=0.9
# )
scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])

collectable = sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)
scene += collectable
agent = sm.SimpleRlAgent(camera_width=64, camera_height=40, position=[0.0, 0.0, 0.0])

scene += agent

reward_function = sm.RewardFunction(
    type="sparse",
    entity_a=agent,
    entity_b=collectable,
    distance_metric="euclidean",
    threshold=1.0,
    is_terminal=True,
    is_collectable=True
)
agent.add_reward_function(reward_function)
timeout_reward_function = sm.RewardFunction(
    type="timeout",
    entity_a=agent,
    entity_b=agent,
    distance_metric="euclidean",
    threshold=500,
    is_terminal=True,
    scalar=-1.0,
)
agent.add_reward_function(timeout_reward_function)

# camera_height = scene.observation_space.shape[1]
# camera_width = scene.observation_space.shape[2]

# get the scene bytes

for i in range(8):
    scene.translate_x(10)
    map_bytes = scene.copy().as_glb_bytes()
    scene.engine.add_to_pool(map_bytes)


scene.activate(4)
camera_height = scene.observation_space.shape[1]
camera_width = scene.observation_space.shape[2]

plt.ion()
fig1, ax1 = plt.subplots()
dummy_obs = np.zeros(shape=(camera_height*2, camera_width*2, 3), dtype=np.uint8)
axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

for i in range(1000):
    actions = [scene.action_space.sample() for _ in range(scene.n_agents)]
    print(actions)
    obs, reward, done, info = scene.step(actions)

    for i in range(2):
        for j in range(2):
            dummy_obs[i*camera_height:(i+1)*camera_height,j*camera_width:(j+1)*camera_width] = obs[i*2+j].transpose(1,2,0)
    axim1.set_data(dummy_obs)
    fig1.canvas.flush_events()
    print(done, reward, info)


scene.close()

