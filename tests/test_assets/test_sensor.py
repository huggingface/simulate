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

import unittest

# Lint as: python3
import numpy as np

import simulate as sm


# TODO add more tests on saving/exporting/loading in gltf files
class ObservationsTest(unittest.TestCase):
    def test_map_sensors_to_spaces(self):
        camera = sm.Camera(height=64, width=64)
        space = camera.observation_space

        self.assertEqual(space.shape, (3, 64, 64))
        self.assertEqual(space.dtype, np.uint8)

        state_sensor = sm.StateSensor(None, None, properties=["position", "distance", "position.x"])
        space = state_sensor.observation_space

        self.assertEqual(space.shape, (5,))
        self.assertEqual(space.dtype, np.float32)

        with self.assertRaises(ValueError):
            _ = sm.StateSensor(None, None, properties=["position", "distance", "position,x"])

    def test_obj_position(self):
        obj = sm.StateSensor()
        self.assertAlmostEqual(obj._position[0], 0)
        self.assertAlmostEqual(obj._position[1], 0)
        self.assertAlmostEqual(obj._position[2], 0)

        self.assertAlmostEqual(obj.position[0], 0)
        self.assertAlmostEqual(obj.position[1], 0)
        self.assertAlmostEqual(obj.position[2], 0)

        obj = sm.StateSensor(position=[1, 1, 1])
        self.assertIsInstance(obj, sm.StateSensor)

        self.assertAlmostEqual(obj._position[0], 1)
        self.assertAlmostEqual(obj._position[1], 1)
        self.assertAlmostEqual(obj._position[2], 1)

        self.assertAlmostEqual(obj.position[0], 1)
        self.assertAlmostEqual(obj.position[1], 1)
        self.assertAlmostEqual(obj.position[2], 1)
