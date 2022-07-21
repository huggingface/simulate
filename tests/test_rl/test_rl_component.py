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


# TODO add more tests on saving/exporting/loading in gltf files
class RlComponentTest(unittest.TestCase):
    def test_create_rl_component(self):

        camera = sm.Camera(width=12, height=12)
        a = sm.Asset(name="a")
        b = sm.Asset(name="b")
        reward = sm.RewardFunction(a, b)
        actions = sm.MappedDiscrete(
            n=3,
            physics=[sm.Physics.ROTATION_Y, sm.Physics.ROTATION_Y, sm.Physics.POSITION_X],
            amplitudes=[-90, 90, 2.0],
        )

        rl_component = sm.RlComponent(actions=actions, observations=camera, rewards=reward)

        self.assertIsInstance(rl_component, sm.RlComponent)

        self.assertIsInstance(rl_component.observations, (list, tuple))
        self.assertIsInstance(rl_component.observation_space, spaces.Space)

        self.assertTrue(len(rl_component.observations) == 1)
        self.assertIsInstance(rl_component.observations[0], sm.Camera)

        self.assertIsInstance(rl_component.action_space, spaces.Space)
        self.assertIsInstance(rl_component.actions, sm.MappedDiscrete)
        self.assertEqual(rl_component.actions, actions)
