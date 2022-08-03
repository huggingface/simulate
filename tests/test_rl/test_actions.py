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
from simenv.rl.actions import ActionMapping


# TODO add more tests on saving/exporting/loading in gltf files
class ActionTest(unittest.TestCase):
    def test_create_mappedbox(self):
        action_map = sm.ActionMapping("move_position", axis=[1, 0, 0])
        action = sm.BoxAction(low=-1.0, high=2.0, action_map=action_map)
        self.assertIsInstance(action, sm.BoxAction)
        self.assertIsInstance(action.action_map, sm.ActionMapping)

        with self.assertRaises(ValueError):
            sm.BoxAction(low=1.0, high=2.0, action_map=[action_map, action_map])

    def test_create_mappeddiscrete(self):
        action_map = [
            sm.ActionMapping("move_position", axis=[1, 0, 0], amplitude=1),
            sm.ActionMapping("move_rotation", axis=[0, 1, 0], amplitude=10),
        ]
        action = sm.DiscreteAction(n=2, action_map=action_map)
        self.assertIsInstance(action, sm.DiscreteAction)
        self.assertIsInstance(action.action_map, list)
        self.assertIsInstance(action.action_map[0], ActionMapping)

        with self.assertRaises(ValueError):
            action = sm.DiscreteAction(n=3, action_map=action_map)
