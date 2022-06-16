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
from typing import Any, Optional

import numpy as np
import pyvista

from ..assets import Asset, Camera, Light, Object3D
from .engine import Engine


try:
    from pyvistaqt import BackgroundPlotter

    # We tweak is a little bit to have Y axis towar the top
    class CustomBackgroundPlotter(BackgroundPlotter):
        def add_toolbars(self) -> None:
            """Add the toolbars."""
            # Camera toolbar
            self.default_camera_tool_bar = self.app_window.addToolBar("Camera Position")

            def _view_vector(*args: Any) -> None:
                return self.view_vector(*args)

            # cvec_setters = {
            #     # Viewing vector then view up vector
            #     "Top (-Z)": lambda: _view_vector((0, 0, 1), (0, 1, 0)),
            #     "Bottom (+Z)": lambda: _view_vector((0, 0, -1), (0, 1, 0)),
            #     "Front (-Y)": lambda: _view_vector((0, 1, 0), (0, 0, 1)),
            #     "Back (+Y)": lambda: _view_vector((0, -1, 0), (0, 0, 1)),
            #     "Left (-X)": lambda: _view_vector((1, 0, 0), (0, 0, 1)),
            #     "Right (+X)": lambda: _view_vector((-1, 0, 0), (0, 0, 1)),
            #     "Isometric": lambda: _view_vector((1, 1, 1), (0, 0, 1)),
            # }

            cvec_setters = {
                # Viewing vector then view up vector
                "Top (-Y)": lambda: _view_vector((0, 1, 0), (0, 0, -1)),
                "Bottom (+Y)": lambda: _view_vector((0, -1, 0), (0, 0, 1)),
                "Front (-Z)": lambda: _view_vector((0, 0, 1), (0, 1, 0)),
                "Back (+Z)": lambda: _view_vector((0, 0, -1), (0, 1, 0)),
                "Left (+X)": lambda: _view_vector((-1, 0, 0), (0, 1, 0)),
                "Right (-X)": lambda: _view_vector((1, 0, 0), (0, 1, 0)),
                "Isometric": lambda: _view_vector((1, 1, 1), (0, 1, 0)),
            }

            for key, method in cvec_setters.items():
                self._view_action = self._add_action(self.default_camera_tool_bar, key, method)
            # pylint: disable=unnecessary-lambda
            self._add_action(self.default_camera_tool_bar, "Reset", lambda: self.reset_camera())

            # Saved camera locations toolbar
            self.saved_camera_positions = []
            self.saved_cameras_tool_bar = self.app_window.addToolBar("Saved Camera Positions")

            self._add_action(self.saved_cameras_tool_bar, "Save Camera", self.save_camera_position)
            self._add_action(
                self.saved_cameras_tool_bar,
                "Clear Cameras",
                self.clear_camera_positions,
            )

except:
    CustomBackgroundPlotter = None


class PyVistaEngine(Engine):
    def __init__(self, scene, auto_update=True, **plotter_kwargs):
        self.plotter: pyvista.Plotter = None
        self.plotter_kwargs = plotter_kwargs
        self.auto_update = bool(CustomBackgroundPlotter is not None and auto_update)

        self._scene: Asset = scene
        self._plotter_actors = {}

    def _initialize_plotter(self):
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.plotter_kwargs)
        if self.auto_update:
            self.plotter: pyvista.Plotter = CustomBackgroundPlotter(**plotter_args)
        else:
            self.plotter: pyvista.Plotter = pyvista.Plotter(**plotter_args)
        # self.plotter.camera_position = "xy"
        self.plotter.view_vector((1, 1, 1), (0, 1, 0))
        self.plotter.add_axes(box=True)

    @staticmethod
    def _get_node_transform(node) -> np.ndarray:
        transforms = list(n.transformation_matrix for n in node.tree_path)
        if len(transforms) > 1:
            model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
        else:
            model_transform_matrix = transforms[0]
        return model_transform_matrix

    def remove_asset(self, asset_node):
        """Remove an asset and all its children in the scene"""
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in asset_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            actor = self._plotter_actors.get(node.uuid)
            if actor is not None:
                self.plotter.remove_actor(actor)

        self.plotter.reset_camera()

    def update_asset(self, asset_node):
        """Add an asset or update its location and all its children in the scene"""
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in asset_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            actor = self._plotter_actors.get(node.uuid)
            if actor is not None:
                self.plotter.remove_actor(actor)

            model_transform_matrix = self._get_node_transform(node)

            self._add_asset_to_scene(node, model_transform_matrix)

        self.plotter.reset_camera()

    def _add_asset_to_scene(self, node, model_transform_matrix):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        if isinstance(node, Object3D):
            # Copying the mesh to located meshes
            located_mesh = node.mesh.transform(model_transform_matrix, inplace=False)
            # Material
            if node.material is None:
                actor = self.plotter.add_mesh(located_mesh)
            else:
                material = node.material
                actor = self.plotter.add_mesh(
                    located_mesh,
                    pbr=material.base_color_texture is None,  # pyvista doesn't support having both a texture and pbr
                    color=material.base_color[:3],
                    opacity=material.base_color[-1],
                    metallic=material.metallic_factor,
                    roughness=material.roughness_factor,
                    texture=material.base_color_texture,
                )

            self._plotter_actors[node.uuid] = actor

        elif isinstance(node, Camera):
            camera = pyvista.Camera()
            camera.model_transform_matrix = model_transform_matrix
            self._plotter_actors[node.uuid] = camera

            self.plotter.camera = camera
        elif isinstance(node, Light):
            light = pyvista.Light()
            light.transform_matrix = model_transform_matrix
            self._plotter_actors[node.uuid] = self.plotter.add_light(light)

    def regenerate_scene(self):
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

        self.plotter.reset_camera()

    def show(self, auto_update: Optional[bool] = None, **pyvista_plotter_kwargs):
        if auto_update is not None and auto_update != self.auto_update:
            self.plotter = None
            self.auto_update = auto_update

        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            self.regenerate_scene()
            self.plotter.show(**pyvista_plotter_kwargs)

    def close(self):
        self.plotter.close()
