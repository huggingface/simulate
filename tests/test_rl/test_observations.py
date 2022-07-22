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
import unittest

import numpy as np

import simenv as sm


# TODO add more tests on saving/exporting/loading in gltf files
class ObservationsTest(unittest.TestCase):
    def test_map_observation_devices_to_spaces(self):
        camera = sm.Camera(height=64, width=64)
        space = sm.map_observation_devices_to_spaces(camera)

        self.assertEqual(space.shape, (3, 64, 64))
        self.assertEqual(space.dtype, np.uint8)
