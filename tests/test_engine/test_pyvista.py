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

import pytest
import pyvista
from pyvista.plotting import system_supports_plotting

import simulate as sm


NO_PLOTTING = not system_supports_plotting()
skip_no_vtk9 = pytest.mark.skipif(pyvista.vtk_version_info < (9,), reason="Requires VTK v9+")

# skip all tests if unable to render
if not system_supports_plotting():
    pytestmark = pytest.mark.skip


@skip_no_vtk9
@pytest.mark.skipif(NO_PLOTTING, reason="Requires system to support plotting")
class PyvistaTest(unittest.TestCase):
    def test_show_scene_pyvista(self):
        scene = sm.Scene(engine="pyvista")
        self.assertIsInstance(scene, sm.Asset)
        self.assertIsInstance(scene.engine, sm.PyVistaEngine)

        scene += sm.Box(position=(-2, 0, 0)) + sm.Sphere(position=(2, 0, 0))
        scene.show(auto_close=False)
        scene.engine.plotter.close()

    def test_show_progressively_scene_pyvista(self):
        scene = sm.Scene(engine="pyvista")
        self.assertIsInstance(scene, sm.Asset)
        self.assertIsInstance(scene.engine, sm.PyVistaEngine)

        scene.show(auto_close=False)
        self.assertEqual(len(scene.engine.plotter.renderer._actors), 0)
        scene.engine.plotter.close()

        scene += sm.Box(position=(-2, 0, 0))
        scene.show(auto_close=False)
        self.assertEqual(len(scene.engine.plotter.renderer._actors), 1)
        scene.engine.plotter.close()

        scene += sm.Sphere(position=(2, 0, 0))
        scene.show(auto_close=False)
        self.assertEqual(len(scene.engine.plotter.renderer._actors), 2)

        # if scene.engine.auto_update:
        #     window = scene.engine.plotter.app_window
        #     self.assertTrue(window.isVisible())

        scene.engine.plotter.close()
