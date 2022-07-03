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

import simenv as sm


class AssetTest(unittest.TestCase):
    def test_create_asset(self):
        asset = sm.Asset()
        self.assertIsInstance(asset, sm.NodeMixin)
        self.assertEqual(asset.name, "asset_00")

        self.assertIsNone(asset.tree_parent)
        self.assertTupleEqual(asset.tree_children, ())

        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))
        np.testing.assert_array_equal(asset.scaling, np.array([1.0, 1.0, 1.0]))

        self.assertIsNone(asset.collider)
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

        asset = sm.Asset().translate_x(2.0)
        np.testing.assert_array_equal(asset.position, np.array([2.0, 0.0, 0.0]))

        asset = sm.Asset().translate_y()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate_y(1)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 1.0, 0.0]))

        asset = sm.Asset().translate_y(2.0)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 2.0, 0.0]))

        asset = sm.Asset().translate_z()
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 0.0]))

        asset = sm.Asset().translate_z(1)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 1.0]))

        asset = sm.Asset().translate_z(2.0)
        np.testing.assert_array_equal(asset.position, np.array([0.0, 0.0, 2.0]))

    def test_rotate_asset(self):
        asset = sm.Asset().rotate()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate((1, 2, 3, 4))
        np.testing.assert_array_equal(asset.rotation, np.array([1.0, 2.0, 3.0, 1.0]))

        asset = sm.Asset().rotate((2.0, 3.0, 4.0, 5.0))
        np.testing.assert_array_equal(asset.rotation, np.array([2.0, 3.0, 4.0, 1.0]))

        asset = sm.Asset().rotate_x()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_x(1)
        np.testing.assert_array_equal(asset.rotation, np.array([1.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_x(2.0)
        np.testing.assert_array_equal(asset.rotation, np.array([2.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_y()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_y(1)
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 1.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_y(2.0)
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 2.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_z()
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 0.0, 1.0]))

        asset = sm.Asset().rotate_z(1)
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 1.0, 1.0]))

        asset = sm.Asset().rotate_z(2.0)
        np.testing.assert_array_equal(asset.rotation, np.array([0.0, 0.0, 2.0, 1.0]))

    def test_scale_asset(self):
        asset = sm.Asset().scale()
        np.testing.assert_array_equal(asset.scaling, np.array([1.0, 1.0, 1.0]))

        asset = sm.Asset().scale(2)
        np.testing.assert_array_equal(asset.scaling, np.array([2.0, 2.0, 2.0]))

        asset = sm.Asset().scale((2.0, 3.0, 4.0))
        np.testing.assert_array_equal(asset.scaling, np.array([2.0, 3.0, 4.0]))
