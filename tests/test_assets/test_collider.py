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
class ColliderTest(unittest.TestCase):
    def test_create_collider(self):
        collider = sm.Collider(bounding_box=[1, 1, 1])
        self.assertIsInstance(collider, sm.Collider)

        child_asset = sm.Asset()
        with self.assertRaises(sm.assets.anytree.TreeError):
            collider += child_asset

    def test_several_colliders(self):
        root = sm.Asset()
        box1 = sm.Box(with_collider=True)
        self.assertTrue(any(isinstance(node, sm.Collider) for node in box1.tree_children))

        box2 = sm.Box(with_collider=True)
        self.assertTrue(any(isinstance(node, sm.Collider) for node in box2.tree_children))

        root += box1
        root += box2
