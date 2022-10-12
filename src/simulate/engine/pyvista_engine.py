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
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import numpy as np
import pyvista

from ..assets import Asset, Camera, Light, Material, Object3D
from ..utils import logging
from .engine import Engine


if TYPE_CHECKING:
    from ..scene import Scene


logger = logging.get_logger(__name__)


try:
    from pyvistaqt import BackgroundPlotter

    # We tweak it a bit to have Y axis toward the top
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

CAMERA_POSITION = [-1, 1, -1]
CAMERA_FOCAL_POINT = [0, 0, 0]
CAMERA_VIEWUP = [0, 1, 0]


class PyVistaEngine(Engine):
    """
    API to render scenes using PyVista.

    Args:
        scene (`Scene`):
            The scene to simulate.
        auto_update (`bool`, *optional*, defaults to `True`):
            Whether to automatically update the scene when an asset is updated.
    """

    def __init__(
        self,
        scene: "Scene",
        auto_update: bool = True,
        **plotter_kwargs: Any,
    ):
        super().__init__(scene, auto_update)
        self.plotter: Union[pyvista.Plotter, None] = None
        self.plotter_kwargs = plotter_kwargs
        self.auto_update = bool(CustomBackgroundPlotter is not None and auto_update)

        self._scene: "Asset" = scene
        self._plotter_actors = {}

    def _initialize_plotter(self):
        """Initialize the plotter to render the scene."""
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.plotter_kwargs)
        if self.auto_update:
            self.plotter: pyvista.Plotter = CustomBackgroundPlotter(**plotter_args)
        else:
            self.plotter: pyvista.Plotter = pyvista.Plotter(**plotter_args)
        self.plotter.camera_position = [CAMERA_POSITION, CAMERA_FOCAL_POINT, CAMERA_VIEWUP]
        if not self.auto_update and hasattr(self.plotter, "add_axes"):
            self.plotter.add_axes(box=True)

    @staticmethod
    def _get_node_transform(node: "Asset") -> np.ndarray:
        """
        Get the transformation matrix of a node.

        Args:
            node (`Asset`):
                The node to get the transformation matrix of.

        Returns:
            `np.ndarray`:
                The transformation matrix of the node.
        """
        transforms = list(n.transformation_matrix for n in node.tree_path)
        if len(transforms) > 1:
            model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
        else:
            model_transform_matrix = transforms[0]
        return model_transform_matrix

    def remove_asset(self, asset_node: "Asset"):
        """
        Remove an asset and all its children in the scene.

        Args:
            asset_node (`Asset`):
                The asset to remove.
        """
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in asset_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            actor = self._plotter_actors.get(node.name)
            if actor is not None and isinstance(actor, (list, tuple)):
                for a in actor:
                    self.plotter.remove_actor(a)
            else:
                self.plotter.remove_actor(actor)

        if hasattr(self.plotter, "reset_camera"):
            self.plotter.reset_camera()

    def update_asset(self, asset_node: "Asset"):
        """
        Add an asset or update its location and all its children in the scene.

        Args:
            asset_node (`Asset`):
                The asset to add or update.
        """
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in asset_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            actor = self._plotter_actors.get(node.name)
            if actor is not None and isinstance(actor, (list, tuple)):
                for a in actor:
                    self.plotter.remove_actor(a)
            else:
                self.plotter.remove_actor(actor)

            model_transform_matrix = self._get_node_transform(node)

            self._add_asset_to_scene(node, model_transform_matrix)

        if hasattr(self.plotter, "reset_camera"):
            self.plotter.reset_camera()

    def _add_asset_to_scene(self, node: "Asset", model_transform_matrix: np.ndarray):
        """
        Add an asset to the scene with a given transform matrix.

        Args:
            node (`Asset`):
                The asset to add.
            model_transform_matrix (`np.ndarray`):
                The transformation matrix of the asset.
        """
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        if isinstance(node, Object3D):
            # We need to handle MultiBlock meshes
            if isinstance(node.mesh, pyvista.MultiBlock):
                located_mesh = [m.transform(model_transform_matrix, inplace=False) for m in node.mesh]
                if isinstance(node.material, (list, tuple)):
                    materials = node.material
                else:
                    materials = [node.material] * len(located_mesh)
            else:
                located_mesh = [node.mesh.transform(model_transform_matrix, inplace=False)]
                materials = [node.material]

            actors = []

            for located_mesh, material in zip(located_mesh, materials):
                if material is None:
                    actor = self.plotter.add_mesh(located_mesh)
                else:
                    material = material
                    actor = self.plotter.add_mesh(
                        located_mesh,
                        pbr=True,  # material.base_color_texture is None, pyvista doesn't support having both texture + pbr
                        color=material.base_color[:3],
                        opacity=material.base_color[-1],
                        metallic=material.metallic_factor,
                        roughness=material.roughness_factor,
                        texture=None,  # We set all the textures ourselves in _set_pbr_material_for_actor
                        specular_power=1.0,  # Fixing a default of pyvista
                        point_size=1.0,  # Fixing a default of pyvista
                    )
                    self._set_pbr_material_for_actor(actor, material)
                actors.append(actor)

            self._plotter_actors[node.name] = actors

        elif isinstance(node, Camera):
            camera = pyvista.Camera()
            camera.model_transform_matrix = model_transform_matrix
            self._plotter_actors[node.name] = camera

            self.plotter.camera = camera
        elif isinstance(node, Light):
            light = pyvista.Light()
            light.transform_matrix = model_transform_matrix
            self._plotter_actors[node.name] = self.plotter.add_light(light)

    @staticmethod
    def _set_pbr_material_for_actor(actor: pyvista._vtk.vtkActor, material: Material):
        """
        Set all the necessary properties for a nice PBR material rendering
        Inspired by https://github.com/Kitware/VTK/blob/master/IO/Import/vtkGLTFImporter.cxx#L188

        Args:
            actor (`pyvista._vtk.vtkActor`):
                The actor to set the material for.
            material (`Material`):
                The PBR material to set.
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
            # set albedo texture
            material.base_color_texture.UseSRGBColorSpaceOn()
            prop.SetBaseColorTexture(material.base_color_texture)

            if material.metallic_roughness_texture:
                # merge ambient occlusion and metallic/roughness, then set material texture
                pbr_texture = material.metallic_roughness_texture.copy()
                pbr_image = pbr_texture.to_image()
                if material.occlusion_texture:
                    # While glTF 2.0 uses two different textures for Ambient Occlusion and Metallic/Roughness
                    # values, VTK only uses one, so we merge both textures into one.
                    # If an Ambient Occlusion texture is present, we merge its first channel into the
                    # metallic/roughness texture (AO is r, Roughness g and Metallic b) If no Ambient
                    # Occlusion texture is present, we need to fill the metallic/roughness texture's first
                    # channel with 255
                    ao_texture = material.occlusion_texture.copy()
                    from vtkmodules.vtkImagingCore import (
                        vtkImageAppendComponents,
                        vtkImageExtractComponents,
                        vtkImageResize,
                    )

                    prop.SetOcclusionStrength(1.0)
                    # If sizes are different, resize the AO texture to the R/M texture's size
                    pbr_size = pbr_image.GetDimensions()
                    ao_image = ao_texture.to_image()
                    ao_size = ao_image.GetDimensions()
                    red_ao = vtkImageExtractComponents()
                    if pbr_size != ao_size:
                        resize = vtkImageResize()
                        resize.SetInputData(ao_image)
                        resize.SetOutputDimensions(pbr_size[0], pbr_size[1], pbr_size[2])
                        resize.Update()
                        red_ao.SetInputConnection(resize.GetOutputPort(0))
                    else:
                        red_ao.SetInputData(ao_image)
                    red_ao.SetComponents(0)
                    gb_pbr = vtkImageExtractComponents()
                    gb_pbr.SetInputData(pbr_image)
                    gb_pbr.SetComponents(1, 2)
                    append = vtkImageAppendComponents()
                    append.AddInputConnection(red_ao.GetOutputPort())
                    append.AddInputConnection(gb_pbr.GetOutputPort())
                    append.SetOutput(pbr_image)
                    append.Update()
                else:
                    pbr_image.GetPointData().GetScalars().FillComponent(0, 255)
                prop.SetORMTexture(pbr_texture)

            if material.emissive_texture:
                material.emissive_texture.UseSRGBColorSpaceOn()
                prop.SetEmissiveTexture(material.emissive_texture)

            if material.normal_texture:
                actor.GetProperty().SetNormalScale(1.0)
                prop.SetNormalTexture(material.normal_texture)

    def regenerate_scene(self):
        """Regenerate the scene from the root node."""
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

        if not self.plotter.renderer.lights and hasattr(self.plotter, "enable_lightkit"):
            self.plotter.enable_lightkit()  # Still add some lights

        if hasattr(self.plotter, "reset_camera"):
            self.plotter.reset_camera()

    def show(self, auto_update: Optional[bool] = None, **plotter_kwargs: Any):
        """
        Show the scene.

        Args:
            auto_update (bool, *optional*, defaults to None):
                Whether the scene will be updated automatically when the scene is modified.
        """
        if auto_update is not None and auto_update != self.auto_update:
            self.plotter = None
            self.auto_update = auto_update

        self.regenerate_scene()
        if self.plotter is not None:
            self.plotter.show(**plotter_kwargs if not self.auto_update else {})

    def close(self):
        """Close the scene."""
        if self.plotter is not None:
            self.plotter.close()

    def reset(self):
        raise NotImplementedError()

    def step(self, action: Optional[Dict] = None, **kwargs: Any) -> Union[Dict, str]:
        raise NotImplementedError()
