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
from typing import Any, Optional, TYPE_CHECKING, List, Dict, Tuple

import sys
import numpy as np
import pyvista

from ..assets import Asset, Camera, Light, Material, Object3D, Collider, RigidBodyComponent, ArticulationBodyComponent, get_trs_from_transform_matrix
from .engine import Engine
from .engine_utils import RedirectStream

with RedirectStream(stream=sys.stderr):
    import pybullet as pb


if TYPE_CHECKING:
    from ..scene import Scene

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


def convert_colliders_to_pybullet(colliders: List[Collider]) -> List[int]:
    pybullet_ids = []
    for collider in colliders:
        if collider.type == "box":
            pybullet_ids.append(
                pb.createCollisionShape(
                    pb.GEOM_BOX,
                    halfExtents=[bound/2 for bound in collider.bounding_box],
                )
            )
        elif collider.type == "sphere":
            pybullet_ids.append(
                pb.createCollisionShape(
                    pb.GEOM_SPHERE,
                    radius=abs(min(collider.bounding_box)/2),
                )
            )
        elif collider.type == "capsule":
            pybullet_ids.append(
                pb.createCollisionShape(
                    pb.GEOM_CAPSULE,
                    radius=collider.bounding_box[0],
                    height=collider.bounding_box[1],
                )
            )
        elif collider.type == "mesh":
            raise NotImplementedError("Mesh collider not implemented yet")
            # pybullet_ids.append(
            #     pb.createCollisionShape(
            #         pb.GEOM_MESH,
            #         fileName=collider.file_name,
            #         meshScale=collider.mesh_scale,
            #     )
            # )
        else:
            raise ValueError(f"Collider type {collider.collider_type} not supported")
    if len(pybullet_ids) == 0:
        return [-1]
    return pybullet_ids


class PyVistaEngine(Engine):
    def __init__(self, scene, auto_update=True, **plotter_kwargs):
        self.plotter: pyvista.Plotter = None
        self.plotter_kwargs = plotter_kwargs
        self.physics_client = None
        self.auto_update = bool(CustomBackgroundPlotter is not None and auto_update)

        self._scene: "Scene" = scene
        self._plotter_actors: Dict[str, Any] = {}
        self._pybullet_actors: Dict[Asset, int] = {}

    def _initialize_plotter(self):
        plotter_args = {"lighting": "none"}
        plotter_args.update(self.plotter_kwargs)
        if self.auto_update:
            self.plotter: pyvista.Plotter = CustomBackgroundPlotter(**plotter_args)
        else:
            self.plotter: pyvista.Plotter = pyvista.Plotter(**plotter_args)
        # self.plotter.camera_position = "xy"
        self.plotter.enable_shadows()
        self.plotter.view_vector((1, 1, 1), (0, 1, 0))
        self.plotter.add_axes(box=True)

    def _initialize_pybullet(self):
        self.physics_client = pb.connect(pb.DIRECT)
        # --- Set some parameters to fix the sticky-walls problem; see
        # https://github.com/bulletphysics/bullet3/issues/3094
        pb.setPhysicsEngineParameter(restitutionVelocityThreshold=0.,
                                    warmStartingFactor=0.,
                                    useSplitImpulse=True,
                                    contactSlop=0.,
                                    enableConeFriction=False,
                                    deterministicOverlappingPairs=True)


    @staticmethod
    def _get_node_transform(node: "Asset") -> np.ndarray:
        transforms = list(n.transformation_matrix for n in node.tree_path)
        print(transforms)
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

            actor = self._plotter_actors.get(node.name)
            if actor is not None:
                self.plotter.remove_actor(actor)
                del self._plotter_actors[node.name]

            pybullet_actor = self._pybullet_actors.get(node)
            if pybullet_actor is not None:
                pb.removeBody(pybullet_actor)
                del self._pybullet_actors[node]

        self.plotter.reset_camera()

    def update_asset(self, asset_node):
        """Add an asset or update its location and all its children in the scene"""
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            return

        for node in asset_node:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            # Remove the actor if it already exists
            actor = self._plotter_actors.get(node.name)
            if actor is not None:
                self.plotter.remove_actor(actor)
                del self._plotter_actors[node.name]

            object_idx = self._pybullet_actors.get(node)
            if object_idx is not None:
                position, rotation, _ = get_trs_from_transform_matrix(self._get_node_transform(node))
                velocity, angular_velocity = pb.getBaseVelocity(object_idx)
                pb.resetBasePositionAndOrientation(object_idx, position, rotation)
                pb.resetBaseVelocity(object_idx, velocity, angular_velocity)

            # Now add it again
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
                    pbr=True,  # material.base_color_texture is None,  # pyvista doesn't support having both a texture and pbr
                    color=material.base_color[:3],
                    opacity=material.base_color[-1],
                    metallic=material.metallic_factor,
                    roughness=material.roughness_factor,
                    texture=None,  # We set all the textures ourself in _set_pbr_material_for_actor
                    specular_power=1.0,  # Fixing a default of pyvista
                    point_size=1.0,  # Fixing a default of pyvista
                )
                self._set_pbr_material_for_actor(actor, material)

            self._plotter_actors[node.name] = actor

            bullet_node_idx = self._pybullet_actors.get(node)
            if bullet_node_idx is None:
                collider_list = [n for n in node.tree_children if isinstance(n, Collider)]
                if len(collider_list) > 0:
                    mass = 0
                    if isinstance(node.physics_component, RigidBodyComponent):
                        mass = node.physics_component.mass if not node.physics_component.kinematic else 0

                    if len(collider_list) > 1:
                        raise NotImplementedError("Compound colliders not implemented yet")
                    collider = collider_list[0]
                    pybullet_collision_shapes = convert_colliders_to_pybullet([collider])
                    base_shape = pybullet_collision_shapes[0]
                    translation, rotation, _ = get_trs_from_transform_matrix(self._get_node_transform(collider))  # position, rotation of the collider

                    bullet_node_idx = pb.createMultiBody(mass,
                                                base_shape,
                                                -1,
                                                translation,
                                                rotation,
                                                useMaximalCoordinates=True)
                    pb.changeDynamics(bullet_node_idx, -1, contactProcessingThreshold=0,
                       spinningFriction=0.001,
                       rollingFriction=0.001,
                       linearDamping=0.0)

                    self._pybullet_actors[node] = bullet_node_idx

            elif isinstance(node.physics_component, ArticulationBodyComponent):
                raise NotImplementedError("Articulation bodies not implemented yet")

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

    def regenerate_scene(self):
        if self.plotter is None or not hasattr(self.plotter, "ren_win"):
            self._initialize_plotter()
        if self.physics_client is None:
            self._initialize_pybullet()

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

    def show(self, auto_update: Optional[bool] = None, **plotter_kwargs):
        if auto_update is not None and auto_update != self.auto_update:
            self.plotter = None
            self.auto_update = auto_update

        self.regenerate_scene()
        self.plotter.show(**plotter_kwargs)

    def step(self, action=None, time_step=None, frame_skip=None, return_nodes=None, return_frames=None, **kwargs):
        if self.physics_client is None:
            self.regenerate_scene()

        if self._scene.config.gravity is not None:
            pb.setGravity(*self._scene.config.gravity)

        time_step = self._scene.config.time_step if time_step is None else time_step
        if time_step is not None:
            pb.setTimeStep(time_step)

        # Run the simulation
        frame_skip = self._scene.config.frame_skip if frame_skip is None else frame_skip
        if frame_skip is not None and frame_skip > 0:
            for _ in range(frame_skip):
                print("run one step")
                pb.stepSimulation()

        # Update new pos/rot the scene
        for node, pybullet_id  in self._pybullet_actors.items():
            pos, rot = pb.getBasePositionAndOrientation(pybullet_id)
            node.position = pos
            node.rotation = rot
        
        # Return the events if needed
        if return_nodes is not None:
            node_dict = {}
            for node in self._scene:
                node_dict[node.name] = {"name": node.name,
                                        "position": node.position,
                                        "rotation": node.rotation}
                if node in self._pybullet_actors:
                    velocity, angular_velocity = pb.getBaseVelocity(self._pybullet_actors[node])
                    node_dict[node.name].update({"velocity": velocity,
                                                 "angular_velocity": angular_velocity})

    def close(self):
        if self.plotter is not None:
            self.plotter.close()

        if self.physics_client is not None:
            try:
                pb.disconnect(self.physics_client)
            except pb.error:
                pass
            self.physics_client = None
