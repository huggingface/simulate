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

import simulate as sm


# this example showcases the rendering and interaction capabilities of the Godot engine

if __name__ == "__main__":

    # create scene (these are familiar boxes without a top used in many examples)
    scene = sm.Scene(engine="godot")
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
    scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
    scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
    scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)
    scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)

    # add green cubes in random locations
    material = sm.Material.GREEN
    for i in range(20):
        scene += sm.Box(
            name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material
        )

    # add one yellow cube
    material = sm.Material.YELLOW
    target = sm.Box(name="cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
    scene += target

    # add an actor
    agent = sm.EgocentricCameraActor(name="agent", position=[0.0, 0.0, 0.0])
    scene += agent

    # wrap the scene to enable interaction
    env = sm.RLEnv(scene)
    env.show()

    # allow the actor to randomly navigate the scene
    for i in range(1000):
        action = agent.rl_component.discrete_actions.sample()
        obs, reward, done, info = env.step(action)

        # NOTE: this example has no reward function!

        plt.pause(0.1)

    scene.close()
