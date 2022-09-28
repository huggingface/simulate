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

import simulate as sm


# TODO add more tests on saving/exporting/loading in gltf files
class RewardsTest(unittest.TestCase):
    def test_create_reward_function(self):
        a = sm.Asset(name="a")
        b = sm.Asset(name="b")
        reward = sm.RewardFunction(entity_a=a, entity_b=b)

        self.assertIsInstance(reward, sm.Asset)
        self.assertIs(reward.entity_a, a)
        self.assertIs(reward.entity_b, b)

    def test_reward_children(self):
        reward = sm.RewardFunction(type="and")
        a = sm.Asset(name="a")
        b = sm.Asset(name="b")
        reward += sm.RewardFunction(entity_a=a, entity_b=b)
        reward += sm.RewardFunction(entity_a=b, entity_b=a)

        scene = sm.Scene()
        scene += reward

        scene += a
        scene -= reward
        scene.a += reward

        self.assertIsInstance(reward, sm.Asset)
        self.assertEqual(len(reward), 2)

        with self.assertRaises(sm.assets.anytree.TreeError):
            reward += b
            scene.show()

    def test_obj_position(self):
        obj = sm.RewardFunction()
        self.assertAlmostEqual(obj._position[0], 0)
        self.assertAlmostEqual(obj._position[1], 0)
        self.assertAlmostEqual(obj._position[2], 0)

        self.assertAlmostEqual(obj.position[0], 0)
        self.assertAlmostEqual(obj.position[1], 0)
        self.assertAlmostEqual(obj.position[2], 0)

        obj = sm.RewardFunction(position=[1, 1, 1])
        self.assertIsInstance(obj, sm.RewardFunction)

        self.assertAlmostEqual(obj._position[0], 1)
        self.assertAlmostEqual(obj._position[1], 1)
        self.assertAlmostEqual(obj._position[2], 1)

        self.assertAlmostEqual(obj.position[0], 1)
        self.assertAlmostEqual(obj.position[1], 1)
        self.assertAlmostEqual(obj.position[2], 1)
