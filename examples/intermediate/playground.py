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


def make_scene(build_exe, camera_width, camera_height):
    scene = sm.Scene(engine="unity", engine_exe=build_exe)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

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

    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    for i in range(1):
        scene += sm.Box(
            name=f"cube{i}",
            position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
            material=material,
            with_collider=True,
        )

    scene += sm.Camera(sensor_tag="SecurityCamera", position=[0, 32, 0], rotation=[90, 0, 0])

    # Let"s add an actor in the scene, a capsule mesh with associated actions and a camera as observation device
    actor = sm.EgocentricCameraActor(
        name="actor", position=[0.0, 0.5, 0.0], camera_tag="CameraSensor"
    )  # Has a collider

    scene += actor
    actor += sm.StateSensor(target_entity=actor, reference_entity=scene.floor, properties="position")
    actor += sm.RaycastSensor(n_horizontal_rays=12, n_vertical_rays=4, horizontal_fov=120, vertical_fov=45)
    # # Let's add a target and a reward function
    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    target = sm.Box(
        name="cube",
        position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
        material=material,
        with_collider=True,
    )
    scene += target

    reward = sm.RewardFunction(type="not")  # By default a dense reward equal to the distance between 2 entities
    reward += sm.RewardFunction(entity_a=target, entity_b=actor)
    actor += reward
    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    args = parser.parse_args()

    camera_width = 40
    camera_height = 40
    scene = make_scene(args.build_exe, camera_width, camera_height)
    print(scene)
    scene.save("test.gltf")

    env = sm.RLEnv(scene)
    env.reset()

    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    # security camera
    fig2, ax2 = plt.subplots()
    dummy_obs2 = np.zeros(shape=(256, 256, 3), dtype=np.uint8)
    axim2 = ax2.imshow(dummy_obs2, vmin=0, vmax=255)

    for i in range(100):
        action = [env.action_space.sample()]
        obs, reward, done, info = env.step(action=action)
        axim1.set_data(obs["CameraSensor"].reshape(3, camera_height, camera_width).transpose(1, 2, 0))
        fig1.canvas.flush_events()
        axim2.set_data(obs["SecurityCamera"].reshape(3, 256, 256).transpose(1, 2, 0))
        fig2.canvas.flush_events()

        plt.pause(0.1)

    scene.close()
