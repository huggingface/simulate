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

import simenv as sm


# TODO add more tests on saving/exporting/loading in gltf files
class ActionTest(unittest.TestCase):
    def test_create_mappedbox(self):
        action = sm.MappedBox(low=-1.0, high=2.0, physics=sm.Physics.POSITION_X)
        self.assertIsInstance(action, sm.MappedBox)
        self.assertIsInstance(action, sm.MappedActions)

        with self.assertRaises(ValueError):
            sm.MappedBox(low=1.0, high=2.0, physics=[sm.Physics.POSITION_X, sm.Physics.POSITION_X])

    def test_create_mappeddiscrete(self):
        action = sm.MappedDiscrete(
            n=3, physics=[sm.Physics.POSITION_X, sm.Physics.ROTATION_Y, sm.Physics.ROTATION_Y], amplitudes=[1, 10, -10]
        )
        self.assertIsInstance(action, sm.MappedDiscrete)
        self.assertIsInstance(action, sm.MappedActions)

        with self.assertRaises(ValueError):
            action = sm.MappedDiscrete(n=3, physics=sm.Physics.POSITION_X)
