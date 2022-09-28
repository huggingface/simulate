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

import numpy as np

import simulate as sm


# From example test at https://github.com/KhronosGroup/glTF-Tutorials/blob/master/gltfTutorial/gltfTutorial_004_ScenesNodes.md
TRANSLATION = [10.0, 20.0, 30.0]
ROTATION = [0.259, 0.0, 0.0, 0.966]
SCALE = [2.0, 1.0, 0.5]
TRANSFORMATION_MAT = np.array(
    [
        [2.0, 0.0, 0.0, 10.0],
        [0.0, 0.86586979, -0.25013472, 20.0],
        [0.0, 0.50026944, 0.43293489, 30.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
)


class AssetTest(unittest.TestCase):
    def test_create_asset(self):
        asset = sm.Asset(name="asset_name")
        self.assertIsInstance(asset, sm.assets.anytree.NodeMixin)
        self.assertEqual(asset.name, "asset_name")

        self.assertIsNone(asset.tree_parent)
        self.assertTupleEqual(asset.tree_children, ())

        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))
        np.testing.assert_array_equal(asset.scaling, np.array([1.0, 1.0, 1.0]))

        self.assertEqual(asset._n_copies, 0)

    def test_translate_asset(self):
        asset = sm.Asset().translate()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate((1, 2, 3))
        np.testing.assert_array_equal(asset.position, np.array([1.0, 2.0, 3.0]))

        asset = sm.Asset().translate((2.0, 3.0, 4.0))
        np.testing.assert_array_equal(asset.position, np.array([2.0, 3.0, 4.0]))

        asset = sm.Asset().translate_x()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate_x(1)
        np.testing.assert_array_equal(asset.position, np.array([1.0, 0.0, 0.0]))

        asset1 = sm.Asset().translate_x(1).translate_x(1)
        asset2 = sm.Asset().translate_x(2.0)
        np.testing.assert_array_equal(asset2.position, np.array([2.0, 0.0, 0.0]))
        np.testing.assert_allclose(asset1.position, asset2.position)

        asset = sm.Asset().translate_y()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate_y(1)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 1.0, 0.0]))

        asset1 = sm.Asset().translate_y(1).translate_y(1)
        asset2 = sm.Asset().translate_y(2.0)
        np.testing.assert_array_equal(asset1.position, np.array([0.0, 2.0, 0.0]))
        np.testing.assert_allclose(asset1.position, asset2.position)

        asset = sm.Asset().translate_z()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate_z(1)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 1.0]))

        asset1 = sm.Asset().translate_z(1).translate_z(1)
        asset2 = sm.Asset().translate_z(2.0)
        np.testing.assert_array_equal(asset1.position, np.array([0.0, 0.0, 2.0]))
        np.testing.assert_allclose(asset1.position, asset2.position)

    def test_rotate_asset(self):
        asset = sm.Asset().rotate_by_quaternion()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_around_vector()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_x()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_y()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_z()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_x(45)
        np.testing.assert_allclose(asset.rotation, np.array([np.sin(np.pi / 8), 0.0, 0.0, np.cos(np.pi / 8)]))

        asset1 = sm.Asset().rotate_x(45).rotate_x(45)
        asset2 = sm.Asset().rotate_x(90)
        np.testing.assert_allclose(asset1.rotation, np.array([np.sin(np.pi / 4), 0.0, 0.0, np.cos(np.pi / 4)]))
        np.testing.assert_allclose(asset1.rotation, asset2.rotation)

        asset = sm.Asset().rotate_y(45)
        np.testing.assert_allclose(asset.rotation, np.array([0.0, np.sin(np.pi / 8), 0.0, np.cos(np.pi / 8)]))

        asset1 = sm.Asset().rotate_y(45).rotate_y(45)
        asset2 = sm.Asset().rotate_y(90)
        np.testing.assert_allclose(asset1.rotation, np.array([0.0, np.sin(np.pi / 4), 0.0, np.cos(np.pi / 4)]))
        np.testing.assert_allclose(asset1.rotation, asset2.rotation)

        asset = sm.Asset().rotate_z(45)
        np.testing.assert_allclose(asset.rotation, np.array([0.0, 0.0, np.sin(np.pi / 8), np.cos(np.pi / 8)]))

        asset1 = sm.Asset().rotate_z(45).rotate_z(45)
        asset2 = sm.Asset().rotate_z(90)
        np.testing.assert_allclose(asset1.rotation, np.array([0.0, 0.0, np.sin(np.pi / 4), np.cos(np.pi / 4)]))
        np.testing.assert_allclose(asset1.rotation, asset2.rotation)

        # Rotate around a diagonal unit axis [1, 1, 1]
        asset = sm.Asset().rotate_around_vector([1, 1, 1], 45)
        quaternion = [
            np.sin(np.pi / 8) / np.sqrt(3),
            np.sin(np.pi / 8) / np.sqrt(3),
            np.sin(np.pi / 8) / np.sqrt(3),
            np.cos(np.pi / 8),
        ]
        np.testing.assert_allclose(asset.rotation, np.array(quaternion))

        # Rotate around a diagonal unit axis [1, 1, 1]
        asset = sm.Asset().rotate_by_quaternion(quaternion)
        np.testing.assert_allclose(asset.rotation, np.array(quaternion))

        # Rotate 2 times around a diagonal unit axis [1, 1, 1]
        asset1 = sm.Asset().rotate_around_vector([1, 1, 1], 45).rotate_around_vector([1, 1, 1], 45)
        asset2 = sm.Asset().rotate_around_vector([1, 1, 1], 90)
        quaternion = [
            np.sin(np.pi / 4) / np.sqrt(3),
            np.sin(np.pi / 4) / np.sqrt(3),
            np.sin(np.pi / 4) / np.sqrt(3),
            np.cos(np.pi / 4),
        ]
        np.testing.assert_allclose(asset1.rotation, np.array(quaternion))
        np.testing.assert_allclose(asset1.rotation, asset2.rotation)

    def test_scale_asset(self):
        asset = sm.Asset().scale()
        np.testing.assert_array_equal(asset.scaling, np.array([1.0, 1.0, 1.0]))

        asset = sm.Asset().scale(2)
        np.testing.assert_array_equal(asset.scaling, np.array([2.0, 2.0, 2.0]))

        asset = sm.Asset().scale(2).scale(2)
        np.testing.assert_array_equal(asset.scaling, np.array([4.0, 4.0, 4.0]))

        asset = sm.Asset().scale((2.0, 3.0, 4.0))
        np.testing.assert_array_equal(asset.scaling, np.array([2.0, 3.0, 4.0]))

    def test_transformation_matrix_asset(self):
        matrix = sm.Asset().transformation_matrix
        np.testing.assert_array_equal(matrix, np.eye(4))

        asset = sm.Asset()
        asset.translate(TRANSLATION)
        asset.rotate_by_quaternion(ROTATION)
        asset.scale(SCALE)
        np.testing.assert_allclose(asset.transformation_matrix, TRANSFORMATION_MAT, rtol=1e-03)

        # When we directly set the transformation matrix
        asset = sm.Asset()  # New asset
        asset.transformation_matrix = TRANSFORMATION_MAT
        np.testing.assert_allclose(asset.position, TRANSLATION, rtol=1e-03)
        np.testing.assert_allclose(asset.rotation, ROTATION, rtol=1e-03)
        np.testing.assert_allclose(asset.scaling, SCALE, rtol=1e-03)

    def test_set_position_asset(self):
        asset = sm.Asset()
        asset.position = [10.0, 20.0, 30.0]
        np.testing.assert_array_equal(asset.position, np.array([10.0, 20.0, 30.0]))
        transformation_mat = np.array(
            [[1.0, 0.0, 0.0, 10.0], [0.0, 1.0, 0.0, 20.0], [0.0, 0.0, 1.0, 30.0], [0.0, 0.0, 0.0, 1.0]]
        )
        np.testing.assert_allclose(asset.transformation_matrix, transformation_mat)

    def test_set_rotation_asset(self):
        asset = sm.Asset()
        asset.rotation = [0.258969, 0.0, 0.0, 0.965886]
        np.testing.assert_allclose(asset.rotation, np.array([0.258969, 0.0, 0.0, 0.965886]), rtol=1e-05)
        transformation_mat = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.86586979, -0.50026944, 0.0],
                [0.0, 0.50026944, 0.86586979, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        np.testing.assert_allclose(asset.transformation_matrix, transformation_mat, rtol=1e-05)

    def test_set_scale_asset(self):
        asset = sm.Asset()
        asset.scaling = [2.0, 1.0, 0.5]
        np.testing.assert_array_equal(asset.scaling, np.array([2.0, 1.0, 0.5]))
        transformation_mat = np.array(
            [[2.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.5, 0.0], [0.0, 0.0, 0.0, 1.0]]
        )
        np.testing.assert_allclose(asset.transformation_matrix, transformation_mat)

    def test_get_asset(self):
        asset = sm.Asset()
        bobby_asset = sm.Asset(name="bobby")
        asset += [bobby_asset, sm.Asset(name="alice")]

        self.assertTrue(hasattr(asset, "bobby"))
        self.assertTrue(hasattr(asset, "alice"))

        get_bobby_asset = asset.get_node("bobby")
        self.assertTrue(bobby_asset is get_bobby_asset)

    def test_copy_asset(self):
        asset = sm.Asset() + [sm.Asset(name="bobby"), sm.Asset(name="alice")]

        self.assertTrue(hasattr(asset, "bobby"))
        self.assertTrue(hasattr(asset, "alice"))

        asset_copy = asset.copy()
        self.assertEqual(len(asset_copy.tree_descendants), 2)
        self.assertTrue(hasattr(asset_copy, "bobby_copy0"))
        self.assertTrue(hasattr(asset_copy, "alice_copy0"))

        self.assertEqual(asset._n_copies, 1)
        self.assertEqual(asset_copy._n_copies, 0)

    def test_enforce_unique_names(self):
        scene = sm.Scene()
        asset = sm.Asset() + [sm.Asset(name="bobby"), sm.Asset(name="alice")]
        bobby2 = sm.Asset(name="bobby")

        with self.assertRaises(ValueError):
            asset += bobby2
            scene += asset
            scene.show()

        bobby2.name = "bobby2"
        asset += bobby2

        with self.assertRaises(ValueError):
            asset.bobby2.name = "bobby"
            scene += asset
            scene.show()
