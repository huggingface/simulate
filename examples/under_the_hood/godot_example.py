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

# Lint as: python3

import argparse
import random

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


# This example showcases how to build a small world, add objects, and add actors to interact with the world.
# The actor must find a randomly colored box labelled `target`.


def make_scene(build_exe):
    scene = sm.Scene(engine="godot")

    # add light to our scene
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    # create the walls of the agent's world
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

    # add a camera to the scene to observe the activity
    scene += sm.Camera(sensor_tag="SecurityCamera", position=[0, 32, 0], rotation=[90, 0, 0])

    # Let's add a default actor in the scene, a capsule mesh with associated actions and a camera as observation device
    # You can create an actor by adding an actuator to an object with physics enabled.
    actor = sm.EgocentricCameraActor(
        name="actor", position=[0.0, 0.5, 0.0], camera_tag="CameraSensor"
    )  # Has a collider by default

    scene += actor

    # add sensors to the actor, so it can understand its position
    actor += sm.StateSensor(target_entity=actor, reference_entity=scene.floor, properties="position")
    actor += sm.RaycastSensor(n_horizontal_rays=12, n_vertical_rays=4, horizontal_fov=120, vertical_fov=45)

    # add a target of a differently colored cube and a reward function
    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    target = sm.Box(
        name="cube",
        position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
        material=material,
        with_collider=True,
    )
    scene += target

    # create a randomly colored cube to distract the actor
    random_material = sm.Material(
        base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]
    )
    scene += sm.Box(
        name=f"cube_random",
        position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
        material=random_material,
        with_collider=True,
    )

    # create a reward function for finding the target cube
    # by default a reward is dense and equal to the distance between 2 entities
    # adding the `not` reward to the distance is like creating a cost between the objects
    reward = sm.RewardFunction(type="not")
    reward += sm.RewardFunction(entity_a=target, entity_b=actor)
    actor += reward
    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    args = parser.parse_args()

    camera_width = 40
    camera_height = 40
    scene = make_scene(args.build_exe)

    # examine the scene we built
    print(scene)
    scene.save("test.gltf")

    # we must wrap our scene with an RLEnv if we want to take actions
    env = sm.RLEnv(scene)

    # reset prepares the environment for stepping
    env.reset()

    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    # security camera
    fig2, ax2 = plt.subplots()
    dummy_obs2 = np.zeros(shape=(256, 256, 3), dtype=np.uint8)
    axim2 = ax2.imshow(dummy_obs2, vmin=0, vmax=255)

    # act!
    for i in range(100):
        action = [env.action_space.sample()]
        obs, reward, done, info = env.step(action=action)
        axim1.set_data(obs["CameraSensor"].reshape(3, camera_height, camera_width).transpose(1, 2, 0))
        fig1.canvas.flush_events()
        axim2.set_data(obs["SecurityCamera"].reshape(3, 256, 256).transpose(1, 2, 0))
        fig2.canvas.flush_events()

        plt.pause(0.1)

    scene.close()
