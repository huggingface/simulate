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

import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt

import simulate as sm


def create_scene(build_exe, size):
    scene = sm.Scene(engine="Unity", engine_exe=build_exe)

    # Set up scene lighting
    scene.config.ambient_color = [1, 1, 1]

    # Load sphere asset and initialize physics components
    radius = 0.045
    sphere_asset = sm.Object3D.create_from("simulate-tests/advanced-physics/Sphere.gltf", scaling=radius)

    # Load hugging face logo from hub
    image_fpath = hf_hub_download(repo_id="simulate-tests/advanced-physics", filename="logo.png", repo_type="space")
    im = np.array(Image.open(image_fpath).resize((size, size))) / 255.0
    height, width = im.shape[:2]

    # Create spheres from hugging face logo
    print("Creating spheres from image")
    spheres_root = sm.Asset(name="spheres_root")
    idx = 0
    mat_dict = {}
    for y in tqdm(range(height)):
        for x in range(width):
            if im[y, x, 3] > 0:
                sphere = sphere_asset.copy()
                sphere.name = f"sphere{idx}"
                sphere += sm.Collider(name=f"sphere{idx}_collider", type="sphere")
                sphere.physics_component = sm.RigidBodyComponent()
                sphere.position = [0.1 * x + 0.05 - width / 20.0, 0.1 * (height - y), 0]
                color = tuple(im[y, x, :3])
                if color in mat_dict:
                    mat = mat_dict[color]
                else:
                    mat = sm.Material(base_color=color)
                    mat_dict[color] = mat
                sphere.material = mat
                spheres_root += sphere
                idx += 1
    scene += spheres_root

    # Create room surrounding spheres
    room = sm.Asset(name="room")
    room += sm.Box(name="floor", scaling=[width * 0.15, 0.1, width * 0.15])
    room += sm.Box(name="ceiling", position=[0, height * 0.125, 0], scaling=[width * 0.15, 0.1, width * 0.15])
    room += sm.Box(name="left_wall", position=[-width * 0.075, height * 0.0625, 0], scaling=[0.1, height * 0.125, width * 0.15])
    room += sm.Box(name="right_wall", position=[width * 0.075, height * 0.0625, 0], scaling=[0.1, height * 0.125, width * 0.15])
    room += sm.Box(name="back_wall", position=[0, height * 0.0625, width * 0.075], scaling=[width * 0.15, height * 0.125, 0.1])
    # We just use a collider with no mesh for the front wall, so that it doesn't block the camera view
    room += sm.Collider(name="front_wall_collider", position=[0, height * 0.0625, -width * 0.075], scaling=[width * 0.15, height * 0.125, 0.1])
    scene += room

    # Set up camera
    scene += sm.Camera(name="camera", width=512, height=512, position=[0, height * 0.05, -width * 0.15])

    scene.show()
    return scene


def simulate(scene, n_frames):
    plt.ion()
    _, ax = plt.subplots(1, 1)
    for i in range(n_frames):
        # Calling scene.step() will step the simulation forward, and return a dictionary of data
        # By default, it contains a rendering from each camera, and node-level data like position and rotation
        event = scene.step()

        # Camera data is provided in shape (CHANNEL, HEIGHT, WIDTH)
        # To display in matplot lib, we tranpose to (HEIGHT, WIDTH, CHANNEL)
        im = np.array(event["frames"]["camera"], dtype=np.uint8).transpose(1, 2, 0)
        ax.clear()
        ax.imshow(im)

        image = Image.fromarray(im)
        image.save(f"output/{i}.png")

        plt.pause(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=90)
    parser.add_argument("-s", "--size", help="square size of the logo", required=False, type=int, default=64)
    args = parser.parse_args()

    scene = create_scene(build_exe=args.build_exe, size=args.size)
    simulate(scene, args.n_frames)

    input("Press enter to continue...")
