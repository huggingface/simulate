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


class PyvistaTest(unittest.TestCase):
    def test_show_scene_pyvista(self):
        scene = sm.Scene(engine="pyvista")
        self.assertIsInstance(scene, sm.Asset)
        self.assertIsInstance(scene.engine, sm.PyVistaEngine)

        scene += sm.Box(position=(-2, 0, 0)) + sm.Sphere(position=(2, 0, 0))
        scene.show()

    def test_show_progressively_scene_pyvista(self):
        scene = sm.Scene(engine="pyvista")
        self.assertIsInstance(scene, sm.Asset)
        self.assertIsInstance(scene.engine, sm.PyVistaEngine)

        scene.show()

        window = scene.engine.plotter.app_window
        renderer = scene.engine.plotter.renderer

        self.assertTrue(window.isVisible())
        self.assertTrue(len(renderer._actors) == 0)

        scene += sm.Box(position=(-2, 0, 0))
        self.assertTrue(len(renderer._actors) == 1)

        scene += sm.Sphere(position=(2, 0, 0))
        self.assertTrue(len(renderer._actors) == 2)
