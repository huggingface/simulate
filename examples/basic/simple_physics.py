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

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


# This example showcases a basic falling object physics experiment


def create_scene(build_exe=""):
    """
    Creates a scene with a floor, falling cube, and necessary components to visualize the scene.
    """

    # Create a scene with Unity engine backend
    scene = sm.Scene(engine="unity", engine_exe=build_exe)
    scene += sm.LightSun()

    # Add a floor
    scene += sm.Box(
        name="floor",
        position=[0, 0, 0],
        bounds=[-10, 10, -0.1, 0, -10, 10],
        material=sm.Material.GRAY75,
    )

    # Add a cube that will fall
    scene += sm.Box(
        name="cube",
        position=[0, 3, 0],
        scaling=[1, 1, 1],
        material=sm.Material.GRAY50,
        with_rigid_body=True,
    )

    # Add a camera to record the scene
    scene += sm.Camera(name="camera", position=[0, 2, -10])

    # Calling show() is required for the scene to be initialized
    scene.show()

    return scene


def simulate(scene, n_frames=60):
    plt.ion()
    _, (ax1, ax2) = plt.subplots(1, 2)
    heights = []
    for i in range(n_frames):
        # Calling scene.step() will step the simulation forward, and return a dictionary of data
        # By default, it contains a rendering from each camera, and node-level data like position and rotation
        event = scene.step()

        # We will graph the height of the cube as it falls
        height = event["nodes"]["cube"]["position"][1]
        heights.append(height)
        ax1.clear()
        ax1.set_xlim([0, n_frames])
        ax1.set_ylim([0, 3])
        ax1.plot(np.arange(len(heights)), heights)

        # Camera data is provided in shape (CHANNEL, HEIGHT, WIDTH)
        # To display in matplot lib, we tranpose to (HEIGHT, WIDTH, CHANNEL)
        im = np.array(event["frames"]["camera"], dtype=np.uint8).transpose(1, 2, 0)
        ax2.clear()
        ax2.imshow(im)

        plt.pause(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=""
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=60)
    args = parser.parse_args()

    build_exe = args.build_exe if args.build_exe != "None" else None
    scene = create_scene(build_exe)
    simulate(scene, args.n_frames)

    input("Press enter to continue...")
