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


if __name__ == "__main__":
    print("First scene")
    scene = sm.Scene()

    # Create mesh
    # Height map and, in the future, a map of simulate objects
    specific_map = (
        np.array(
            [
                [[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
                [[[1, 1], [0, 0]], [[1, 1], [1, 1]]],
                [[[0, 0], [0, 0]], [[0, 0], [0, 0]]],
            ]
        )
        * 0.6
    )

    scene += sm.ProcGenGrid(specific_map=specific_map)
    scene += sm.LightSun()
    scene.show()

    input("Press Enter for second scene")
    scene.close()
    scene.clear()

    # Second scene: generating from this map
    scene += sm.ProcGenGrid(width=3, height=3, sample_map=specific_map)
    scene += sm.LightSun()
    scene.show()

    input("Press Enter for third scene")
    scene.close()
    scene.clear()

    # Ideally, instead of "hardcoding" the tiles, you would create a function
    # to generate them
    tiles = 0.6 * np.array([[[i, i, i], [i, i, i], [i, i, i]] for i in range(2)])

    # Weights and symmetries are facultative
    weights = [1.0 - i * 0.5 for i in range(2)]
    symmetries = ["X"] * 2

    # Create constraints that define which tiles can be neighbors
    neighbors = [(tiles[1], tiles[0]), (tiles[0], tiles[0]), (tiles[1], tiles[1])]
    scene += sm.ProcGenGrid(
        width=3, height=3, tiles=tiles, neighbors=neighbors, weights=weights, symmetries=symmetries
    )
    scene += sm.LightSun()

    scene.show()
    input("Press Enter to close")

    scene.close()
