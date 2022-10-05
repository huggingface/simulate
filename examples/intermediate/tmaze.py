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

import time

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


# this example showcases building a small detailed maze for an agent to explore


if __name__ == "__main__":
    CAMERA_HEIGHT = 40
    CAMERA_WIDTH = 64

    scene = sm.Scene(engine="unity")

    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
    scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])

    agent = sm.EgocentricCameraActor(
        camera_width=CAMERA_WIDTH, camera_height=CAMERA_HEIGHT, position=[0.0, 0.0, 0.0], camera_tag="CameraSensor"
    )

    scene += agent
    scene.show()
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    env = sm.RLEnv(scene)
    env.reset()

    for i in range(1000):
        action = env.sample_action()
        obs, reward, done, info = env.step(action)
        axim1.set_data(np.squeeze(obs["CameraSensor"]).transpose(1, 2, 0))
        fig1.canvas.flush_events()

        time.sleep(0.1)

    scene.close()
