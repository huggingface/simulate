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
from typing import ByteString, List, Set, Union
from dataclasses import asdict

import numpy as np
import PIL.Image
from trimesh import Trimesh

# from trimesh.path.entities import Line  # Line need scipy
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

from simenv.gltflib.models import material

from .assets import Asset, Camera, DirectionalLight, Object, PointLight, SpotLight
from .gltflib import GLTF, GLTFModel, Material
from .gltflib.enums import AccessorType, ComponentType, PrimitiveMode


# Conversion of gltf dtype and shapes in Numpy equivalents
gltf_to_numpy_dtypes_mapping = {
    ComponentType.BYTE: np.dtype("<i1"),
    ComponentType.UNSIGNED_BYTE: np.dtype("<u1"),
    ComponentType.SHORT: np.dtype("<i2"),
    ComponentType.UNSIGNED_SHORT: np.dtype("<u2"),
    ComponentType.UNSIGNED_INT: np.dtype("<u4"),
    ComponentType.FLOAT: np.dtype("<f4"),
}

gltf_to_numpy_shapes_mapping = {
    AccessorType.SCALAR: 1,
    AccessorType.VEC2: (2,),
    AccessorType.VEC3: (3,),
    AccessorType.VEC4: (4,),
    AccessorType.MAT2: (2, 2),
    AccessorType.MAT3: (3, 3),
    AccessorType.MAT4: (4, 4),
}


# A couple of data extraction methods
def get_buffer_as_bytes(gltf_scene: GLTF, buffer_view_id: int) -> ByteString:
    """Get a ByteString of the data stored in a GLTF buffer view"""
    gltf_model = gltf_scene.model

    buffer_view = gltf_model.bufferViews[buffer_view_id]
    buffer = gltf_model.buffers[buffer_view.buffer]
    ressource = gltf_scene.get_resource(buffer.uri)
    if not ressource.loaded:
        ressource.load()

    byte_offset = buffer_view.byteOffset
    length = buffer_view.byteLength

    data = ressource.data[byte_offset : byte_offset + length]

    return data


def get_image_as_bytes(gltf_scene: GLTF, image_id: int) -> ByteString:
    """Get a ByteString of the data stored in a GLTF image"""
    gltf_model = gltf_scene.model

    image = gltf_model.images[image_id]
    if image.bufferView is not None:
        return get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=image.bufferView)

    ressource = gltf_scene.get_resource(image.uri)
    if not ressource.loaded:
        ressource.load()

    return ressource.data


def get_accessor_as_numpy(gltf_scene: GLTF, accessor_id: int) -> np.ndarray:
    """Get a numpy array of the data stored in a GLTF accessor"""
    gltf_model = gltf_scene.model
    accessor = gltf_model.accessors[accessor_id]

    dtype: np.dtype = gltf_to_numpy_dtypes_mapping[accessor.componentType]
    item_shape = gltf_to_numpy_shapes_mapping[accessor.type]
    total_shape = np.append(accessor.count, item_shape)
    total_size = np.abs(np.product(total_shape))

    if accessor.sparse is not None:
        raise NotImplementedError
    else:
        data = get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=accessor.bufferView)
        array = np.frombuffer(buffer=data, offset=accessor.byteOffset, count=total_size, dtype=dtype)
        array = array.reshape(total_shape)

    return array


def get_texture_as_pillow(gltf_scene: GLTF, texture_id: int) -> PIL.Image:
    gltf_textures = gltf_scene.model.textures
    gltf_images = gltf_scene.model.images
    gltf_samplers = gltf_scene.model.samplers

    gltf_texture = gltf_textures[texture_id]
    gltf_image = gltf_images[gltf_texture.source]

    if gltf_image.bufferView is not None:
        data = get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=gltf_image.bufferView)
    else:
        ressource = gltf_scene.get_resource(gltf_image.uri)
        if not ressource.loaded:
            ressource.load()
        data = ressource.data

    image = PIL.Image.open(data)  # TODO checkk all this image stuff

    return image


def get_material_as_trimesh(gltf_scene: GLTF, material_id: int) -> PBRMaterial:
    """Get a trimesh material of the material stored in a GLTF scene"""
    gltf_materials = gltf_scene.model.materials
    gltf_material = gltf_materials[material_id]

    pbrMetallicRoughness = {}
    if gltf_material.pbrMetallicRoughness is not None:
        pbrMetallicRoughness = deepcopy(asdict(gltf_material.pbrMetallicRoughness))
        del pbrMetallicRoughness["extensions"]
        del pbrMetallicRoughness["extras"]

    other_keys = deepcopy(asdict(gltf_material))
    del other_keys["pbrMetallicRoughness"]
    del other_keys["extensions"]
    del other_keys["extras"]

    # Load images if needed
    full_dict = dict(**pbrMetallicRoughness, **other_keys)
    for key in full_dict:
        if isinstance(full_dict[key], dict) and "index" in full_dict[key]:
            texture_id = full_dict[key]["index"]
            full_dict[key] = get_texture_as_pillow(gltf_scene=gltf_scene, texture_id=texture_id)

    material = PBRMaterial(
        **full_dict
    )  # TODO maybe loss of precision when converting to trimesh (uint8 for baseColor for instance - to check)

    return material


# Build a tree of simenv nodes from a GLTF object
def build_node_tree(gltf_scene: GLTF, gltf_node_id: int, parent=None) -> List:
    """Build the node tree of simenv objects from the GLTF scene"""
    gltf_model = gltf_scene.model
    gltf_node = gltf_model.nodes[gltf_node_id]
    common_kwargs = {
        "name": gltf_node.name,
        "translation": gltf_node.translation,
        "rotation": gltf_node.rotation,
        "parent": parent,
    }

    scene_nodes_list = []

    if gltf_node.camera is not None:
        # Let's add a Camera
        gltf_camera = gltf_model.cameras[gltf_node.camera]
        camera_type = gltf_camera.type
        scene_node = Camera(
            aspect_ratio=gltf_camera.perspective.aspectRatio,
            yfov=gltf_camera.perspective.yfov,
            zfar=gltf_camera.perspective.zfar if camera_type == "perspective" else gltf_camera.orthographic.zfar,
            znear=gltf_camera.perspective.znear if camera_type == "perspective" else gltf_camera.orthographic.znear,
            camera_type=camera_type,
            xmag=gltf_camera.orthographic.xmag if camera_type == "orthographic" else None,
            ymag=gltf_camera.orthographic.ymag if camera_type == "orthographic" else None,
            **common_kwargs,
        )

    elif gltf_node.extensions.KHR_lights_punctual is not None:
        # Let's add a light
        gltf_light_id = gltf_node.extensions.KHR_lights_punctual.light
        gltf_light = gltf_model.extensions.KHR_lights_punctual.lights[gltf_light_id]
        if gltf_light.type == "directional":
            scene_node = DirectionalLight(
                intensity=gltf_light.intensity, color=gltf_light.color, range=gltf_light.range, **common_kwargs
            )
        elif gltf_light.type == "point":
            scene_node = PointLight(
                intensity=gltf_light.intensity, color=gltf_light.color, range=gltf_light.range, **common_kwargs
            )
        elif gltf_light.type == "spot":
            scene_node = SpotLight(
                intensity=gltf_light.intensity, color=gltf_light.color, range=gltf_light.range, **common_kwargs
            )
        else:
            raise ValueError(
                f"Unrecognized GLTF file light type: {gltf_light.type}, please check that the file is conform with the KHR_lights_punctual specifications"
            )

    elif gltf_node.mesh is not None:
        # Let's add a mesh
        gltf_mesh = gltf_model.meshes[gltf_node.mesh]
        primitives = gltf_mesh.primitives
        for primitive in primitives:
            attributes = primitive.attributes
            vertices = get_accessor_as_numpy(gltf_scene=gltf_scene, accessor_id=attributes.POSITION)
            if primitive.mode == PrimitiveMode.POINTS:
                trimesh_primitive = Trimesh(vertices=vertices)
            elif primitive.mode == PrimitiveMode.LINES:
                raise NotImplementedError()  # Using Line in trimesh reauires scipy
                # trimesh_primitive = Trimesh(vertices=vertices, entities=[Line(points=np.arange(len(vertices)))])
            elif primitive.mode in [PrimitiveMode.TRIANGLES, PrimitiveMode.TRIANGLE_STRIP]:
                # Faces
                faces = None
                if primitive.indices is None:
                    faces = np.arange(len(vertices), dtype=np.int64).reshape((-1, 3))
                else:
                    faces = get_accessor_as_numpy(gltf_scene=gltf_scene, accessor_id=primitive.indices)
                if primitive.mode == PrimitiveMode.TRIANGLE_STRIP:
                    raise NotImplementedError()

                # Vertex normals
                vertex_normals = None
                if attributes.NORMAL is not None:
                    vertex_normals = get_accessor_as_numpy(gltf_scene=gltf_scene, accessor_id=attributes.NORMAL)

                # TODO we are not handling "tangent" at the moment

                # Visuals/vertex colors
                visual = None
                vertex_colors = None
                if primitive.material is not None:
                    material = get_material_as_trimesh(gltf_scene=gltf_scene, material_id=primitive.material)
                    uv = get_accessor_as_numpy(gltf_scene=gltf_scene, accessor_id=attributes.TEXCOORD_0).copy()

                    # From trimesh - trimesh.exchange.gltf.py
                    # flip UV's top- bottom to move origin to lower-left:
                    # https://github.com/KhronosGroup/glTF/issues/1021
                    uv[:, 1] = 1.0 - uv[:, 1]
                    # create a texture visual
                    visual = TextureVisuals(uv=uv, material=material)

                    if attributes.COLOR_0 is not None:
                        colors = get_accessor_as_numpy(gltf_scene=gltf_scene, accessor_id=attributes.COLOR_0)
                        if len(colors) == len(vertices):
                            visual.vertex_attributes["color"] = colors
                            vertex_colors = colors

                # TODO metadata are not included at the moment

                trimesh_primitive = Trimesh(
                    vertices=vertices,
                    faces=faces,
                    vertex_normals=vertex_normals,
                    vertex_colors=vertex_colors,
                    visual=visual,
                )

            else:
                raise NotImplementedError()

            scene_node = Object(**common_kwargs, mesh=trimesh_primitive)  # we create an object and link it
            scene_nodes_list.append(scene_node)

    else:
        # We just have an empty node with a transform
        scene_node = Asset(**common_kwargs)

    if not scene_nodes_list:
        scene_nodes_list = [
            scene_node
        ]  # for the meshes primitives we've built the list already, for the other we build it here

    # Recursively build the node tree
    if gltf_node.children:
        for child_id in gltf_node.children:
            scene_child_nodes = build_node_tree(gltf_scene=gltf_scene, gltf_node_id=child_id, parent=scene_node)
            scene_nodes_list += scene_child_nodes

    return scene_nodes_list


def load_gltf_in_assets(file_path) -> List[Asset]:
    """Loading function to create a Scene from a GLTF file"""
    gltf_scene = GLTF.load(file_path)
    gltf_model = gltf_scene.model

    main_scene = gltf_model.scenes[gltf_model.scene if gltf_model.scene else 0]
    main_nodes = main_scene.nodes

    assets = []

    for main_node_id in main_nodes:
        assets += build_node_tree(gltf_scene=gltf_scene, gltf_node_id=main_node_id, parent=None)

    return assets
