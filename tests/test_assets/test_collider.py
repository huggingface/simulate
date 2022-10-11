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

import pyvista as pv

# Lint as: python3
from pyvista.examples import download_bunny

import simulate as sm


# TODO add more tests on saving/exporting/loading in gltf files
class ColliderTest(unittest.TestCase):
    def test_create_collider(self):
        scene = sm.Scene()
        collider = sm.Collider(bounding_box=[1, 1, 1])
        self.assertIsInstance(collider, sm.Collider)

        child_asset = sm.Asset()
        with self.assertRaises(sm.assets.anytree.TreeError):
            collider += child_asset
            scene += collider
            scene.show()

    def test_create_asset_collider(self):
        mesh = download_bunny()
        asset = sm.Object3D(name="object", mesh=mesh)

        asset.build_collider()

        self.assertIsInstance(asset.tree_children[0], sm.Collider)
        self.assertIsInstance(asset.tree_children[0].mesh, pv.MultiBlock)
        self.assertEqual(len(asset.tree_children[0].mesh), 16)

    def test_several_colliders(self):
        root = sm.Asset()
        box1 = sm.Box(with_collider=True)
        self.assertTrue(any(isinstance(node, sm.Collider) for node in box1.tree_children))

        box2 = sm.Box(with_collider=True)
        self.assertTrue(any(isinstance(node, sm.Collider) for node in box2.tree_children))

        root += box1
        root += box2

    def test_obj_position(self):
        obj = sm.Collider()
        self.assertAlmostEqual(obj._position[0], 0)
        self.assertAlmostEqual(obj._position[1], 0)
        self.assertAlmostEqual(obj._position[2], 0)

        self.assertAlmostEqual(obj.position[0], 0)
        self.assertAlmostEqual(obj.position[1], 0)
        self.assertAlmostEqual(obj.position[2], 0)

        obj = sm.Collider(position=[1, 1, 1])
        self.assertIsInstance(obj, sm.Collider)

        self.assertAlmostEqual(obj._position[0], 1)
        self.assertAlmostEqual(obj._position[1], 1)
        self.assertAlmostEqual(obj._position[2], 1)

        self.assertAlmostEqual(obj.position[0], 1)
        self.assertAlmostEqual(obj.position[1], 1)
        self.assertAlmostEqual(obj.position[2], 1)
