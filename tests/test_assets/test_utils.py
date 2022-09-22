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


class UtilsTest(unittest.TestCase):
    def test_camelcase_to_snakecase(self):
        string = "ThisIsACamelCaseString"
        self.assertEqual(sm.utils.camelcase_to_snakecase(string), "this_is_a_camel_case_string")

    def test_snakecase_to_camelcase(self):
        string = "this_is_a_snake_case_string"
        self.assertEqual(sm.utils.snakecase_to_camelcase(string), "ThisIsASnakeCaseString")

    def test_transformation_matrix_and_trs_conversion_functions(self):

        matrix = sm.utils.get_transform_from_trs(TRANSLATION, ROTATION, SCALE)
        trs = sm.utils.get_trs_from_transform_matrix(TRANSFORMATION_MAT)

        np.testing.assert_allclose(matrix, TRANSFORMATION_MAT, rtol=1e-03)
        np.testing.assert_allclose(trs[0], TRANSLATION, rtol=1e-03)
        np.testing.assert_allclose(trs[1], ROTATION, rtol=1e-03)
        np.testing.assert_allclose(trs[2], SCALE, rtol=1e-03)

    def test_get_product_of_quaternions(self):
        q1 = [0.0, 0.0, 0.0, 1.0]
        q2 = [0.0, 0.0, 0.0, 1.0]
        q3 = sm.utils.get_product_of_quaternions(q1, q2)
        np.testing.assert_allclose(q3, [0.0, 0.0, 0.0, 1.0], rtol=1e-03)

        q1 = np.array([0.0, np.sin(np.pi / 8), 0.0, np.cos(np.pi / 8)])
        q2 = np.array([0.0, np.sin(np.pi / 8), 0.0, np.cos(np.pi / 8)])
        q3 = sm.utils.get_product_of_quaternions(q1, q2)
        np.testing.assert_allclose(q3, np.array([0.0, np.sin(np.pi / 4), 0.0, np.cos(np.pi / 4)]), rtol=1e-03)

    def test_rotation_from_euler_radians(self):
        euler = [0.0, 0.0, 0.0]
        rotation = sm.utils.rotation_from_euler_radians(*euler)
        np.testing.assert_allclose(rotation, [0.0, 0.0, 0.0, 1.0], rtol=1e-03)

        euler = [0.0, 0.0, np.pi / 2]
        rotation = sm.utils.rotation_from_euler_radians(*euler)
        np.testing.assert_allclose(rotation, [0.0, 0.0, np.sin(np.pi / 4), np.cos(np.pi / 4)], rtol=1e-03)

    def test_rotation_from_euler_degrees(self):
        euler = [0.0, 0.0, 90.0]
        rotation = sm.utils.rotation_from_euler_degrees(*euler)
        np.testing.assert_allclose(rotation, [0.0, 0.0, np.sin(np.pi / 4), np.cos(np.pi / 4)], rtol=1e-03)
