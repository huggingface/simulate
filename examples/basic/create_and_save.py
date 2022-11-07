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

import simulate as sm


# This example showcases basic scene assembly and saving as a gltf
if __name__ == "__main__":

    # creates a basic scene and saves as gltf
    scene = sm.Scene(engine="pyvista")

    # add light source
    scene += sm.LightSun()

    # add objects to scene
    scene += [sm.Sphere(position=[1, 0, 0], with_collider=True), sm.Box(name="target", position=[0, 2.5, 0])]

    # the print function returns a tree for scene
    print(scene)
    # This should return the following
    # Scene(engine='PyVistaEngine')
    # ├── light_sun_00(LightSun)
    # ├── sphere_00(Sphere)
    # │   └── sphere_00_collider(Collider)
    # └── target(Box)
    # └── target_collider(Collider)

    # save the scene
    scene.save("output/test.gltf")

    scene.show()

    input("Press enter to end this example.")
