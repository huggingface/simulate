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

from ..assets import Asset, Camera, Light, Material, Object3D
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

except ImportError:
    CustomBackgroundPlotter = None


class PyVistaEngine(Engine):
    def __init__(self, scene, auto_update=True, **add_mesh_kwargs):
        self.plotter: pyvista.Plotter = None
        self.add_mesh_kwargs = add_mesh_kwargs
        self.auto_update = bool(CustomBackgroundPlotter is not None and auto_update)

        self._scene: Asset = scene
        self._plotter_actors = {}

    def _initialize_plotter(self):
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.add_mesh_kwargs)
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

    def _add_asset_to_scene(self, node, model_transform_matrix, **add_mesh_kwargs):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        if isinstance(node, Object3D):
            # Copying the mesh to located meshes
            located_mesh = node.mesh.transform(model_transform_matrix, inplace=False)
            # Material
            if node.material is None:
                actor = self.plotter.add_mesh(located_mesh, **add_mesh_kwargs)
            else:
                material = node.material
                actor = self.plotter.add_mesh(
                    located_mesh,
                    pbr=True,  # material.base_color_texture is None,  # pyvista doesn't support having both a texture and pbr
                    color=material.base_color[:3],
                    opacity=material.base_color[-1],
                    metallic=material.metallic_factor,
                    roughness=material.roughness_factor,
                    texture=None,  # We set all the textures ourself in _set_pbr_material_for_actor
                    specular_power=1.0,  # Fixing a default of pyvista
                    point_size=1.0,  # Fixing a default of pyvista
                    **add_mesh_kwargs,
                )
                self._set_pbr_material_for_actor(actor, material, located_mesh)

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

    @staticmethod
    def _set_pbr_material_for_actor(actor: pyvista._vtk.vtkActor, material: Material, mesh: pyvista.DataSet):
        """Set all the necessary properties for a nice PBR material rendering
        Inspired by https://github.com/Kitware/VTK/blob/master/IO/Import/vtkGLTFImporter.cxx#L188
        """
        from vtkmodules.vtkCommonCore import vtkInformation
        from vtkmodules.vtkRenderingCore import vtkProp

        prop = actor.GetProperty()
        if material.alpha_mode != "OPAQUE":
            prop.ForceTranslucentOn()
        # flip texture coordinates
        if actor.GetPropertyKeys() is None:
            info = vtkInformation()
            actor.SetPropertyKeys(info)
        mat = [1, 0, 0, 0, 0, -1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]
        actor.GetPropertyKeys().Set(vtkProp.GeneralTextureTransform(), mat, 16)

        if not material.double_sided:
            actor.GetProperty().BackfaceCullingOn()

        if material.base_color_texture:
            if mesh.GetPointData().GetTCoords() is None:
                raise ValueError(
                    "This mesh doesn't have texture coordinates. "
                    "You need to define them to use a texture. "
                    "You can set texture coordinate with mesh.active_t_coords."
                )
            # set albedo texture
            material.base_color_texture.UseSRGBColorSpaceOn()
            prop.SetBaseColorTexture(material.base_color_texture)

            if material.metallic_roughness_texture:
                # merge ambient occlusion and metallic/roughness, then set material texture
                pbrTexture = material.metallic_roughness_texture.copy()
                pbrImage = pbrTexture.to_image()
                if material.occlusion_texture:
                    # While glTF 2.0 uses two different textures for Ambient Occlusion and Metallic/Roughness
                    # values, VTK only uses one, so we merge both textures into one.
                    # If an Ambient Occlusion texture is present, we merge its first channel into the
                    # metallic/roughness texture (AO is r, Roughness g and Metallic b) If no Ambient
                    # Occlusion texture is present, we need to fill the metallic/roughness texture's first
                    # channel with 255
                    aoTexture = material.occlusion_texture.copy()
                    from vtkmodules.vtkImagingCore import (
                        vtkImageAppendComponents,
                        vtkImageExtractComponents,
                        vtkImageResize,
                    )

                    prop.SetOcclusionStrength(1.0)
                    # If sizes are different, resize the AO texture to the R/M texture's size
                    pbrSize = pbrImage.GetDimensions()
                    aoImage = aoTexture.to_image()
                    aoSize = aoImage.GetDimensions()
                    redAO = vtkImageExtractComponents()
                    if pbrSize != aoSize:
                        resize = vtkImageResize()
                        resize.SetInputData(aoImage)
                        resize.SetOutputDimensions(pbrSize[0], pbrSize[1], pbrSize[2])
                        resize.Update()
                        redAO.SetInputConnection(resize.GetOutputPort(0))
                    else:
                        redAO.SetInputData(aoImage)
                    redAO.SetComponents(0)
                    gbPbr = vtkImageExtractComponents()
                    gbPbr.SetInputData(pbrImage)
                    gbPbr.SetComponents(1, 2)
                    append = vtkImageAppendComponents()
                    append.AddInputConnection(redAO.GetOutputPort())
                    append.AddInputConnection(gbPbr.GetOutputPort())
                    append.SetOutput(pbrImage)
                    append.Update()
                else:
                    pbrImage.GetPointData().GetScalars().FillComponent(0, 255)
                prop.SetORMTexture(pbrTexture)

            if material.emissive_texture:
                material.emissive_texture.UseSRGBColorSpaceOn()
                prop.SetEmissiveTexture(material.emissive_texture)

            if material.normal_texture:
                actor.GetProperty().SetNormalScale(1.0)
                prop.SetNormalTexture(material.normal_texture)

    def regenerate_scene(self, **add_mesh_kwargs):
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

            self._add_asset_to_scene(node, model_transform_matrix, **add_mesh_kwargs)

        if not self.plotter.renderer.lights:
            self.plotter.enable_lightkit()  # Still add some lights

        self.plotter.reset_camera()

    def show(self, auto_update: Optional[bool] = None, **kwargs):
        if auto_update is not None and auto_update != self.auto_update:
            self.plotter = None
            self.auto_update = auto_update

        auto_close = kwargs.pop("auto_close", True)
        if isinstance(self.plotter, pyvista.Plotter):
            plotter_kwargs = {"auto_close": auto_close}
        else:
            plotter_kwargs = {}

        self.regenerate_scene(**kwargs)
        self.plotter.show(**plotter_kwargs)

    def close(self):
        if self.plotter is not None:
            self.plotter.close()
