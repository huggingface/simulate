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

import simulate as sm


def create_scene(build_exe="", size=32):
    # scene = sm.Scene(engine="unity", engine_exe=build_exe)
    scene = sm.Scene()
    scene += sm.LightSun()

    sphere_asset = sm.Object3D.create_from("simulate-tests/advanced-physics/Sphere.gltf")
    print(sphere_asset)
    scene += sphere_asset

    """ image_fpath = hf_hub_download(repo_id="simulate-tests/advanced-physics", filename="logo.png", repo_type="space")
    im = np.array(Image.open(image_fpath).resize((size, size))) / 255.0
    height, width = im.shape[:2]
    print("Creating spheres from image")
    for y in tqdm(range(height)):
        for x in range(width):
            if im[y, x, 3] > 0:
                scene += sm.Sphere(position=[x, height - y, 0], radius=0.5) """

    scene.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=""
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    parser.add_argument("-s", "--size", help="square size of the logo", required=False, type=int, default=16)
    args = parser.parse_args()

    scene = create_scene(build_exe=args.build_exe, size=args.size)

    input("Press enter to continue...")
