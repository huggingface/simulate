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

from gym import spaces

import simenv as sm
from simenv.assets import camera


# TODO add more tests on saving/exporting/loading in gltf files
class RlComponentTest(unittest.TestCase):
    def test_create_rl_component(self):
        camera = sm.Camera(height=64, width=64)
        camera_sensor = sm.CameraSensor(camera=camera)
        a = sm.Asset(name="a")
        b = sm.Asset(name="b")
        reward = sm.RewardFunction(a, b)
        actions = sm.DiscreteAction(
            n=3,
            action_map=[
                sm.ActionMapping("move_position", [1, 0, 0], 2.0),
                sm.ActionMapping("move_rotation", [0, 1, 0], -90),
                sm.ActionMapping("move_rotation", [0, 0, 1], 90),
            ],
        )

        rl_component = sm.RlComponent(discrete_actions=actions, camera_sensors=camera_sensor, reward_functions=reward)

        self.assertIsInstance(rl_component, sm.RlComponent)

        self.assertIsInstance(rl_component.camera_sensors, (list, tuple))
        # self.assertIsInstance(rl_component.observation_space, spaces.Space)

        self.assertTrue(len(rl_component.camera_sensors) == 1)
        self.assertIsInstance(rl_component.camera_sensors[0], sm.CameraSensor)

        self.assertIsInstance(rl_component.action_space, spaces.Space)
        self.assertIsInstance(rl_component.discrete_actions, sm.DiscreteAction)
        self.assertEqual(rl_component.discrete_actions, actions)
