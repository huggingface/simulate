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
import io
from copy import deepcopy
from dataclasses import asdict
from typing import ByteString, List, Optional, Set, Union

import numpy as np
import PIL.Image
import pyvista as pv

from .assets import Asset, Camera, Light, Object3D
from .gltflib import GLTF, GLTFModel
from .gltflib.enums import AccessorType, ComponentType, PrimitiveMode
from .gltflib.models.material import Material


# TODO remove this GLTFReader once the new version of pyvista is released 0.34+ (included in it)
class GLTFReader(pv.utilities.reader.BaseReader):
    """GLTFeader for .gltf and .glb files.

    Examples
    --------
    >>> reader = GLTFReader(filename)
    >>> mesh = reader.read()  # A MultiBlock reproducing the hierarchy of Nodes in the GLTF file
    """

    _class_reader = pv._vtk.vtkGLTFReader


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
    resource = gltf_scene.get_resource(buffer.uri)
    if not resource.loaded:
        resource.load()

    byte_offset = buffer_view.byteOffset
    length = buffer_view.byteLength

    data = resource.data[byte_offset : byte_offset + length]

    return data


def get_image_as_bytes(gltf_scene: GLTF, image_id: int) -> ByteString:
    """Get a ByteString of the data stored in a GLTF image"""
    gltf_model = gltf_scene.model

    image = gltf_model.images[image_id]
    if image.bufferView is not None:
        return get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=image.bufferView)

    resource = gltf_scene.get_resource(image.uri)
    if not resource.loaded:
        resource.load()

    return resource.data


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
        resource = gltf_scene.get_resource(gltf_image.uri)
        if not resource.loaded:
            resource.load()
        data = resource.data

    image = PIL.Image.open(io.BytesIO(data))  # TODO checkk all this image stuff

    return image


# Build a tree of simenv nodes from a GLTF object
def build_node_tree(
    gltf_scene: GLTF, pyvista_meshes: pv.MultiBlock, gltf_node_id: int, parent: Optional[Asset] = None
) -> List:
    """Build the node tree of simenv objects from the GLTF scene"""
    gltf_model = gltf_scene.model
    gltf_node = gltf_model.nodes[gltf_node_id]
    common_kwargs = {
        "name": gltf_node.name,
        "center": gltf_node.translation,
        "direction": gltf_node.rotation,
        "scale": gltf_node.scale,
        "parent": parent,
    }

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

    elif gltf_node.extensions is not None and gltf_node.extensions.KHR_lights_punctual is not None:
        # Let's add a light
        gltf_light_id = gltf_node.extensions.KHR_lights_punctual.light
        gltf_light = gltf_model.extensions.KHR_lights_punctual.lights[gltf_light_id]
        if gltf_light.type == "directional":
            scene_node = Light(
                light_type="directional",
                intensity=gltf_light.intensity,
                color=gltf_light.color,
                range=gltf_light.range,
                **common_kwargs,
            )
        elif gltf_light.type == "point":
            scene_node = Light(
                light_type="positional",
                intensity=gltf_light.intensity,
                color=gltf_light.color,
                range=gltf_light.range,
                **common_kwargs,
            )
        elif gltf_light.type == "spot":
            scene_node = Light(
                light_type="positional",
                inner_cone_angle=np.degrees(gltf_light.innerConeAngle),
                outer_cone_angle=np.degrees(gltf_light.outerConeAngle),
                intensity=gltf_light.intensity,
                color=gltf_light.color,
                range=gltf_light.range,
                **common_kwargs,
            )
        else:
            raise ValueError(
                f"Unrecognized GLTF file light type: {gltf_light.type}, please check that the file is conform with the KHR_lights_punctual specifications"
            )

    elif gltf_node.mesh is not None:
        # Let's add a mesh
        gltf_mesh = gltf_model.meshes[gltf_node.mesh]
        n_primitives = len(gltf_mesh.primitives)
        for index in range(n_primitives):
            mesh = pyvista_meshes[f"Mesh_{gltf_node.mesh}"][index]
            scene_node = Object3D(**common_kwargs, mesh=mesh)
    else:
        # We just have an empty node with a transform
        scene_node = Asset(**common_kwargs)

    # Recursively build the node tree
    if gltf_node.children:
        for child_id in gltf_node.children:
            _ = build_node_tree(
                gltf_scene=gltf_scene,
                pyvista_meshes=pyvista_meshes[f"Node_{child_id}"],
                gltf_node_id=child_id,
                parent=scene_node,
            )

    return scene_node


def load_gltf_as_tree(file_path) -> List[Asset]:
    """Loading function to create a tree of asset nodes from a GLTF file.
    Return a list of the main nodes in the GLTF files (often only one main node).
    The tree can be walked from the main nodes.
    """
    pyvista_reader = GLTFReader(
        file_path
    )  # We load the meshe already converted by pyvista/vtk instead of decoding our self
    pyvista_reader.reader.ApplyDeformationsToGeometryOff()  # We don't want to apply the transforms to the various nodes
    pyvista_meshes = pyvista_reader.read()
    gltf_scene = GLTF.load(file_path)  # We load the other nodes (camera, lights, our extensions) ourselves
    gltf_model = gltf_scene.model

    gltf_main_scene = gltf_model.scenes[gltf_model.scene if gltf_model.scene else 0]
    gltf_main_nodes = gltf_main_scene.nodes

    main_nodes = []

    for gltf_node_id in gltf_main_nodes:
        main_nodes.append(
            build_node_tree(
                gltf_scene=gltf_scene,
                pyvista_meshes=pyvista_meshes[f"Node_{gltf_node_id}"],
                gltf_node_id=gltf_node_id,
                parent=None,
            )
        )

    return main_nodes
