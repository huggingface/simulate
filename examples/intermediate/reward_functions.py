# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


# this example showcases different varieties of reward functions that can be added to one scene.


if __name__ == "__main__":

    # initialize a scene and a light source
    scene = sm.Scene(engine="unity")
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    # create a room in the scene
    scene += sm.Box(
        name="floor",
        position=[0, 0, 0],
        bounds=[-50, 50, 0, 0.1, -50, 50],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    scene += sm.Box(
        name="wall1",
        position=[-10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.RED,
        with_collider=True,
    )
    scene += sm.Box(
        name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED, with_collider=True
    )
    scene += sm.Box(
        name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED, with_collider=True
    )
    scene += sm.Box(
        name="wall4",
        position=[0, 0, -10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.RED,
        with_collider=True,
    )

    # add one randomly colored box
    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    scene += sm.Box(
        name="cube1",
        position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
        material=material,
        with_collider=True,
    )

    # Let's create an actor in the scene, a capsule mesh with associated actions and a camera as observation device
    actor = sm.Capsule(name="actor", is_actor=True, position=[0.0, 0.7, 0.0], with_collider=True)  # Has a collider
    actor.physics_component = sm.RigidBodyComponent(constraints=["freeze_rotation_x", "freeze_rotation_z"])

    # Specify the action to control the actor: 3 discrete action to rotate and move forward
    actor.actuator = sm.Actuator(
        n=3,
        mapping=[
            sm.ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=-10),
            sm.ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=10),
            sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=0.1),
        ],
    )
    scene += actor

    # Add a camera located on the actor
    actor_camera = sm.Camera(name="camera", width=40, height=40, position=[0, 0.75, 0])
    actor += actor_camera
    actor += sm.StateSensor(target_entity=actor, reference_entity=actor_camera, properties="position")

    # Add a target for a reward function
    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    target = sm.Box(name="cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
    scene += target

    # add an and reward function for the target and itself and the target and itself (for instruction purposes)
    and_reward = sm.RewardFunction(type="and")
    and_child1 = sm.RewardFunction(type="sparse", entity_a=target, entity_b=actor)
    and_child2 = sm.RewardFunction(type="sparse", entity_a=target, entity_b=target)
    # this children logic is required for or / and / other logical reward predicates
    and_reward += [and_child1, and_child2]
    actor += and_reward

    # add reward functions for being both near and far to the target
    or_reward = sm.RewardFunction(type="or")
    # dense rewards return the distance
    or_child1 = sm.RewardFunction(type="dense", entity_a=target, entity_b=actor)
    # adding a not to dense reward makes it a cost on distance
    or_child2 = sm.RewardFunction(type="not")
    or_child2 += sm.RewardFunction(type="dense", entity_a=target, entity_b=actor)
    # add or children
    or_reward += [or_child1, or_child2]
    actor += or_reward

    # add visual reward!
    not_reward = sm.RewardFunction(type="not")
    not_reward += sm.RewardFunction(type="see", entity_a=target, entity_b=actor)
    actor += not_reward

    # add a timeout reward! This will return a reward after a threshold
    timeout_reward = sm.RewardFunction(type="timeout")
    actor += timeout_reward

    print(scene)
    scene.save("test.gltf")

    # wrap the scene in an environment, so we can observe rewards
    env = sm.RLEnv(scene)

    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(actor.camera.height, actor.camera.width, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    for i in range(1000):
        obs, reward, done, info = env.step(env.sample_action())
        print(f"reward {reward}")
        obs = np.squeeze(obs["CameraSensor"]).transpose(1, 2, 0)
        axim1.set_data(obs)
        fig1.canvas.flush_events()

        plt.pause(0.1)

    scene.close()
