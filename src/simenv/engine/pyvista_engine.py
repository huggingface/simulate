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
""" A PyVista plotting rendered as engine."""
from typing import Optional

import numpy as np
import pyvista
from matplotlib.pyplot import plot

from ..assets import Asset, Camera, Light, Object3D
from .engine import Engine


class PyVistaEngine(Engine):
    def __init__(self, scene, **plotter_kwargs):
        self.plotter: pyvista.Plotter = None
        self.plotter_kwargs = plotter_kwargs
        self._scene: Asset = scene
        self._initialize_plotter()

    def _initialize_plotter(self):
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.plotter_kwargs)
        self.plotter: pyvista.Plotter = pyvista.Plotter(**plotter_args)
        self.plotter.camera_position = "xy"
        self.plotter.add_axes(box=True)

    def _update_scene(self):
        if not hasattr(self.plotter, "ren_win"):
            self._initialize_plotter()
        self.plotter.clear()

        has_lights = False
        for node in self._scene:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            transforms = list(n.transform for n in node.tree_path)
            if len(transforms) > 1:
                model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
            else:
                model_transform_matrix = transforms[0]

            if isinstance(node, Object3D):
                located_mesh = node.mesh.transform(model_transform_matrix, inplace=False)
                self.plotter.add_mesh(located_mesh)
            elif isinstance(node, Camera):
                camera = pyvista.Camera()
                camera.model_transform_matrix = model_transform_matrix
                self.plotter.camera = camera
            elif isinstance(node, Light):
                light = pyvista.Light()
                light.transform_matrix = model_transform_matrix
                self.plotter.add_light(light)
                has_lights = True
        if not has_lights:
            self.plotter.enable_lightkit()  # Still add some lights

    def show(self, **pyvista_plotter_kwargs):
        self._update_scene()

        if "cpos" not in pyvista_plotter_kwargs:
            pyvista_plotter_kwargs["cpos"] = "xy"

        self.plotter.show(**pyvista_plotter_kwargs)

    def close(self):
        self.plotter.close()
