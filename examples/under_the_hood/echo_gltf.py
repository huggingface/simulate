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

import argparse
import base64

import simulate as sm


# this example showcases how Simulate can duplicate gltf data


def create_scene(build_exe=""):

    # load a scene from the tests (locally here, but also can use the hub)
    scene = sm.Scene(engine="unity", engine_exe=build_exe)
    scene.load("simulate-tests/Box/glTF-Embedded/Box.gltf")

    scene.show()

    return scene


def echo_gltf(scene):
    # convert the gltf of the scene to raw data and verify with the engine
    bytes = scene.as_glb_bytes()
    b64_bytes = base64.b64encode(bytes).decode("ascii")
    result = scene.engine.run_command("TestEchoGLTF", b64bytes=b64_bytes)
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=""
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)
    echo_gltf(scene)

    input("Press any key to continue...")
