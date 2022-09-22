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


# TODO add more tests on saving/exporting/loading gltf cameras in gltf files
class CameraTest(unittest.TestCase):
    def test_create_camera(self):
        camera = sm.Camera()
        self.assertIsInstance(camera, sm.Camera)

    def test_create_distant_camera(self):
        camera = sm.CameraDistant()
        self.assertIsInstance(camera, sm.CameraDistant)
