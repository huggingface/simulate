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

import numpy as np

import simulate as sm


# This example tests the StructuredGrid object in Simulate
if __name__ == "__main__":
    scene = sm.Scene(engine="unity")

    # Create mesh data
    x = np.arange(-5, 5, 0.25)
    z = np.arange(-5, 5, 0.25)
    x, z = np.meshgrid(x, z)
    r = np.sqrt(x**2 + z**2)
    y = np.sin(r)

    # convert the array to a 3d object
    scene += sm.StructuredGrid(x, y, z)

    # add a lightsun for rendering
    scene += sm.LightSun()
    scene += sm.Camera(position=[0, 5, -15], rotation=[0, 1, 0, 0])
    scene.show()

    input("Press enter to end this example.")
    scene.close()
