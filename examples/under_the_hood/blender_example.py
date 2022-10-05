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

import simulate as sm


# This example shows how a scene can be rendered with the Blender animation tool.


def create_scene():
    # create a scene with the blender engine
    scene = sm.Scene(engine="blender")

    # load an asset from the hub
    scene += sm.Asset.create_from("simulate-tests/Chair/glTF-Binary/SheenChair.glb", name="chair")

    # add light and a camera
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)
    scene += sm.Camera(name="cam1", position=[2, 3, 2], rotation=[-45, 45, 0], width=1024, height=1024)
    scene.show()

    # optional scene saving as image: uncomment to render the scene to an image in the desired folder
    # scene.render(path="")
    scene.close()


if __name__ == "__main__":
    create_scene()
