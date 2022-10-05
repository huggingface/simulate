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


# This examples showcases the different objects we have in HuggingFace Simulate
if __name__ == "__main__":
    scene = sm.Scene()
    scene += sm.LightSun()
    # Create Plane as the base of our example
    scene += sm.Plane()

    # a Sphere will center our objects
    center = sm.Sphere(position=[0, 1, 0], material=sm.Material.RED)

    # it will be bordered by a rotated capsule, rotated on all axes
    # it is a child of sphere, so it is in relative coordinates
    center += sm.Capsule(position=[2, 0, 0], rotation=[30, 30, 30], material=sm.Material.WHITE)

    # add a Cylinder too
    center += sm.Cylinder(position=[-2, 0, 0], material=sm.Material.GREEN)

    # Box
    center += sm.Box(position=[0, 0, 2], material=sm.Material.BLUE)

    # Cone
    center += sm.Cone(position=[0, 0, -2], material=sm.Material.CYAN)

    # Line
    center += sm.Line(position=[2, 0, -2], material=sm.Material.MAGENTA)

    # Tube
    center += sm.Tube(position=[2, 0, 2], material=sm.Material.TEAL)

    # Ring
    center += sm.Ring(position=[-2, 0, 2], material=sm.Material.PURPLE)

    # Text3D
    center += sm.Text3D(position=[0, 2, 0], string="HF Rocks!", rotation=[135, 135, 180], material=sm.Material.YELLOW)

    # Triangle
    center += sm.Triangle(position=[-2, 0, -2], material=sm.Material.OLIVE)

    scene += center
    print(scene)
    scene.show()

    input("Press enter to end the example!")
