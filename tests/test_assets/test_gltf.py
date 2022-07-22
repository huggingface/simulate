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

import os
import tempfile

# Lint as: python3
import unittest

import numpy as np

import simenv as sm


FIXTURE_BOX_FILE = os.path.join(os.path.dirname(__file__), "fixtures", "Box.gltf")


class GltfTest(unittest.TestCase):
    def test_create_asset_from_gltf_in_scene(self):
        scene = sm.Scene.create_from(FIXTURE_BOX_FILE)
        self.assertEqual(len(scene), 1)

        child = scene.tree_children[0]
        self.assertTrue(hasattr(scene, child.name))
        self.assertEqual(child.mesh.n_points, 24)
        self.assertEqual(child.material.base_color, [0.800000011920929, 0.0, 0.0, 1.0])

    def test_load_asset_from_gltf_in_scene(self):
        scene = sm.Scene()
        scene.load(FIXTURE_BOX_FILE)
        self.assertEqual(len(scene), 1)

        child = scene.tree_children[0]
        self.assertTrue(hasattr(scene, child.name))
        self.assertEqual(child.mesh.n_points, 24)
        self.assertEqual(child.material.base_color, [0.800000011920929, 0.0, 0.0, 1.0])

    def test_save_asset_in_gltf_from_scene(self):
        scene = sm.Scene.create_from(FIXTURE_BOX_FILE)
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.gltf")
            scene.save(file_path)
            self.assertTrue(os.path.exists(file_path))

            gltf_original_scene = sm.assets.gltflib.GLTF.load(FIXTURE_BOX_FILE)
            gltf_saved_scene = sm.assets.gltflib.GLTF.load(file_path)

            self.assertEqual(len(gltf_original_scene.model.nodes), len(gltf_saved_scene.model.nodes))

            scene2 = sm.Scene.create_from(file_path)
            self.assertFalse(scene == scene2)
            np.testing.assert_array_equal(scene.tree_children[0].mesh.points, scene2.tree_children[0].mesh.points)
            np.testing.assert_array_equal(
                scene.tree_children[0].transformation_matrix, scene2.tree_children[0].transformation_matrix
            )

    def test_create_asset_from_gltf_in_asset(self):
        asset = sm.Asset().create_from(FIXTURE_BOX_FILE)
        child = asset.tree_children[0]
        self.assertEqual(child.mesh.n_points, 24)
        self.assertEqual(child.material.base_color, [0.800000011920929, 0.0, 0.0, 1.0])

    def test_load_asset_from_gltf_in_asset(self):
        asset = sm.Asset()
        asset.load(FIXTURE_BOX_FILE)
        child = asset.tree_children[0]
        self.assertEqual(child.mesh.n_points, 24)
        self.assertEqual(child.material.base_color, [0.800000011920929, 0.0, 0.0, 1.0])

    def test_save_asset_in_gltf_from_asset(self):
        asset = sm.Asset.create_from(FIXTURE_BOX_FILE)
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.gltf")
            asset.save(file_path)
            self.assertTrue(os.path.exists(file_path))

            gltf_original_asset = sm.assets.gltflib.GLTF.load(FIXTURE_BOX_FILE)
            gltf_saved_asset = sm.assets.gltflib.GLTF.load(file_path)

            self.assertEqual(len(gltf_original_asset.model.nodes), len(gltf_saved_asset.model.nodes))

            asset2 = sm.Scene.create_from(file_path)
            self.assertFalse(asset == asset2)
            np.testing.assert_array_equal(asset.tree_children[0].mesh.points, asset2.tree_children[0].mesh.points)
            np.testing.assert_array_equal(
                asset.tree_children[0].transformation_matrix, asset2.tree_children[0].transformation_matrix
            )
