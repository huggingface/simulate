import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


scene = sm.Scene(engine="unity")
scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)
scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)

material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
for i in range(1):
    scene += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

# Lets add an actor in the scene, a capsule mesh with associated actions and a camera as observation device
actor = sm.Capsule(name="actor", position=[0.0, 0.0, 0.0])  # Has a collider
# Specify the action to control the actor: 3 discrete action to rotate and move forward
actor.controller = sm.Controller(
    n=3,
    mapping=[
        sm.ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=-90),
        sm.ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=90),
        sm.ActionMapping("change_relative_position", axis=[1, 0, 0], amplitude=2.0),
    ],
)
scene += actor

# Add a camera located on the actor
actor_camera = sm.Camera(name="camera", width=40, height=40, position=[0, 0.75, 0])
actor += actor_camera
actor += sm.StateSensor(target_entity=actor, reference_entity=actor_camera, properties="position")

# # Let's add a target and a reward function
material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
target = sm.Box(name="cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
scene += target


and_reward = sm.RewardFunction(type="and")
and_child1 = sm.RewardFunction(type="sparse", entity_a=target, entity_b=actor)
and_child2 = sm.RewardFunction(type="sparse", entity_a=target, entity_b=target)
and_reward += [and_child1, and_child2]
actor += and_reward

or_reward = sm.RewardFunction(type="or")
or_child1 = sm.RewardFunction(type="dense", entity_a=target, entity_b=actor)
or_child2 = sm.RewardFunction(type="not")
or_child2 += sm.RewardFunction(type="dense", entity_a=target, entity_b=actor)
or_reward += [or_child1, or_child2]
actor += or_reward

not_reward = sm.RewardFunction(type="not")  # By default a dense reward equal to the distance between 2 entities
not_reward += sm.RewardFunction(type="see", entity_a=target, entity_b=actor)
actor += not_reward

timeout_reward = sm.RewardFunction(type="timeout")
actor += timeout_reward

print(scene)
scene.save("test.gltf")

env = sm.ParallelRLEnvironment(scene)

# plt.ion()
# fig1, ax1 = plt.subplots()
# dummy_obs = np.zeros(shape=(actor.camera.height, actor.camera.width, 3), dtype=np.uint8)
# axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

for i in range(1000):
    obs, reward, done, info = env.step()


# # for i in range(1000):
# #     obs, reward, done, info = env.step()
# #     obs = obs[actor_camera.name].transpose(1, 2, 0)  # (C,H,W) -> (H,W,C)
# #     axim1.set_data(obs)
# #     fig1.canvas.flush_events()

#     plt.pause(0.1)

# scene.close()
