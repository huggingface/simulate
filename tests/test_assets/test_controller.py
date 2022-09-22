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

from simulate.assets.actuator import ActionMapping, Actuator


# TODO add more tests on saving/exporting/loading in gltf files
class ActionTest(unittest.TestCase):
    def test_create_mappedbox(self):
        mapping = [
            ActionMapping("change_position", axis=[1, 0, 0]),
            ActionMapping("change_position", axis=[0, 1, 0]),
        ]
        action = Actuator(low=-1.0, high=2.0, shape=(2,), mapping=mapping)
        self.assertIsInstance(action, Actuator)
        self.assertIsInstance(action.mapping, list)
        self.assertIsInstance(action.mapping[0], ActionMapping)

        with self.assertRaises(ValueError):
            Actuator(low=1.0, high=2.0, mapping=[mapping, mapping])

    def test_create_mappeddiscrete(self):
        mapping = [
            ActionMapping("change_position", axis=[1, 0, 0], amplitude=1),
            ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=10),
        ]
        action = Actuator(n=2, mapping=mapping)
        self.assertIsInstance(action, Actuator)
        self.assertIsInstance(action.mapping, list)
        self.assertIsInstance(action.mapping[0], ActionMapping)

        with self.assertRaises(ValueError):
            action = Actuator(n=3, mapping=mapping)
