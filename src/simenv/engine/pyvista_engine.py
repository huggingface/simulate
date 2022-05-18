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


try:
    from pyvistaqt import BackgroundPlotter
except:
    BackgroundPlotter = None


class PyVistaEngine(Engine):
    def __init__(self, scene, disable_background_plotter=False, **plotter_kwargs):
        self.plotter: pyvista.Plotter = None
        self.plotter_kwargs = plotter_kwargs
        self._background_plotter = bool(BackgroundPlotter is not None and not disable_background_plotter)

        self._scene: Asset = scene
        self._plotter_actors = {}

    def _initialize_plotter(self):
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.plotter_kwargs)
        if self._background_plotter:
            self.plotter: pyvista.Plotter = BackgroundPlotter(**plotter_args)
        else:
            self.plotter: pyvista.Plotter = pyvista.Plotter(**plotter_args)
        self.plotter.camera_position = "xy"
        self.plotter.add_axes(box=True)

    def update_asset_in_scene(self, root_node):
        """Update the location of an asset and all its children in the scene"""
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in root_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            transforms = list(n.transformation_matrix for n in node.tree_path)
            if len(transforms) > 1:
                model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
            else:
                model_transform_matrix = transforms[0]

            actor = self._plotter_actors.get(node)
            if actor is not None:
                self.plotter.remove_actor(actor)

            self._add_asset_to_scene(node, model_transform_matrix)

    def _add_asset_to_scene(self, node, model_transform_matrix):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        if isinstance(node, Object3D):
            # Copying the mesh to located meshes
            located_mesh = node.mesh.transform(model_transform_matrix, inplace=False)
            self._plotter_actors[node] = self.plotter.add_mesh(located_mesh)

        elif isinstance(node, Camera):
            camera = pyvista.Camera()
            camera.model_transform_matrix = model_transform_matrix
            self._plotter_actors[node] = camera

            self.plotter.camera = camera
        elif isinstance(node, Light):
            light = pyvista.Light()
            light.transform_matrix = model_transform_matrix
            self._plotter_actors[node] = self.plotter.add_light(light)

    def recreate_scene(self):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            self._initialize_plotter()

        # Clear plotter and dict of located meshes
        self.plotter.clear()
        self._plotter_actors = {}

        for node in self._scene:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            transforms = list(n.transformation_matrix for n in node.tree_path)
            if len(transforms) > 1:
                model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
            else:
                model_transform_matrix = transforms[0]

            self._add_asset_to_scene(node, model_transform_matrix)

        if not self.plotter.renderer.lights:
            self.plotter.enable_lightkit()  # Still add some lights

    def show(self, **pyvista_plotter_kwargs):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            self.recreate_scene()
            self.plotter.show(**pyvista_plotter_kwargs)

    def close(self):
        self.plotter.close()
