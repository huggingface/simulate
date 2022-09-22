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


PREDEFINED_MATERIALS = [
    "RED",
    "GREEN",
    "BLUE",
    "CYAN",
    "MAGENTA",
    "YELLOW",
    "BLACK",
    "WHITE",
    "GRAY",
    "GRAY25",
    "GRAY50",
    "GRAY75",
    "TEAL",
    "PURPLE",
    "OLIVE",
]

DEFAULT_COLOR = [1.0, 1.0, 1.0, 1.0]


# TODO add more tests on saving/exporting/loading in gltf files
class MaterialssTest(unittest.TestCase):
    def test_create_material(self):
        material = sm.Material()
        self.assertIsInstance(material, sm.Material)

        self.assertListEqual(material.base_color, DEFAULT_COLOR)

    def test_create_predefined_materials(self):
        for material_name in PREDEFINED_MATERIALS:
            self.assertIn(material_name, sm.Material.__dict__)
            material = getattr(sm.Material, material_name)
            self.assertIsInstance(material, sm.Material)

            if material_name != "WHITE":
                self.assertTrue(
                    any(color not in DEFAULT_COLOR for color in material.base_color),
                    msg=f"{material_name} has an issue",
                )
