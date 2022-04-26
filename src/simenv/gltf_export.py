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
""" Load a GLTF file in a Scene."""
from copy import deepcopy
from typing import ByteString, List, Set

import numpy as np
import PIL.Image
import trimesh
from trimesh.exchange.gltf import export_glb

# from trimesh.path.entities import Line  # Line need scipy
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

from simenv.gltflib.models import material

from .assets import (
    Asset,
    Camera,
    Capsule,
    Cube,
    Cylinder,
    DirectionalLight,
    Object,
    PointLight,
    Primitive,
    Sphere,
    SpotLight,
)
from .gltflib import GLTF, GLTFModel, Material
from .gltflib.enums import AccessorType, ComponentType, PrimitiveMode


def add_node_tree_to_scene(node: Asset, trimesh_scene: trimesh.Scene, parent_node_name=None) -> trimesh.Scene:
    if isinstance(node, Object):
        geometry = None
        if isinstance(node, Sphere):
            geometry = (
                trimesh.creation.uv_sphere()
            )  # TODO we will want this mesh creation at the initialization of the object and inside the object __init__, not when sending the object
        elif isinstance(node, Capsule):
            geometry = trimesh.creation.capsule()
        elif isinstance(node, Cylinder):
            geometry = trimesh.creation.cylinder(1)
        elif isinstance(node, Cube):
            geometry = trimesh.creation.box()
        else:
            print(f"Primitive type {node.primitive_type} not implemented for Trimesh view")
        if geometry is not None:
            trimesh_scene.add_geometry(
                geometry=geometry, node_name=node.name, parent_node_name=None
            )  # TODO we won't be using trimesh for gltf export

    if node.children is not None:
        for child in node.children:
            trimesh_scene = add_node_tree_to_scene(
                child, trimesh_scene, parent_node_name=None
            )  #  TODO recreate this parent thing

    return trimesh_scene


def export_assets_to_gltf(root_node: Asset) -> dict:
    trimesh_scene = trimesh.Scene()
    trimesh_scene = add_node_tree_to_scene(root_node, trimesh_scene=trimesh_scene)
    return export_glb(trimesh_scene)
