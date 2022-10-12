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
""" Export a Scene as a GLTF file."""
import hashlib
from typing import Any, ByteString, Dict, List, Optional, Set, Union

import numpy as np
import pyvista as pv

from ..config import Config
from . import Asset, Camera, Collider, Light, Material, Object3D, PhysicMaterial
from . import gltflib as gl
from .gltf_extension import GLTF_NODES_EXTENSION_CLASS, process_tree_after_gltf, process_tree_before_gltf


# Conversion of Numpy dtype and shapes in GLTF equivalents
NP_FLOAT32 = np.dtype("<f4")
NP_UINT32 = np.dtype("<u4")
NP_UINT8 = np.dtype("<u1")

numpy_to_gltf_dtypes_mapping = {
    np.dtype("<i1"): gl.ComponentType.BYTE,
    np.dtype("<u1"): gl.ComponentType.UNSIGNED_BYTE,
    np.dtype("<i2"): gl.ComponentType.SHORT,
    np.dtype("<u2"): gl.ComponentType.UNSIGNED_SHORT,
    np.dtype("<u4"): gl.ComponentType.UNSIGNED_INT,
    np.dtype("<f4"): gl.ComponentType.FLOAT,
}

numpy_to_gltf_shapes_mapping = {
    (1,): gl.AccessorType.SCALAR,
    (2,): gl.AccessorType.VEC2,
    (3,): gl.AccessorType.VEC3,
    (4,): gl.AccessorType.VEC4,
    (2, 2): gl.AccessorType.MAT2,
    (3, 3): gl.AccessorType.MAT3,
    (4, 4): gl.AccessorType.MAT4,
}


def _get_digest(data: Any) -> bytes:
    """
    Get a hash digest of the data.

    Args:
        data (`Any`):
            The data to hash.

    Returns:
        digest (`bytes`):
            The hash digest of the data.
    """
    if isinstance(data, (Material, PhysicMaterial)):
        digest = str(hash(data)).encode("utf-8")
    else:
        h = hashlib.md5()
        if isinstance(data, pv.Texture):
            data_pointer = np.ascontiguousarray(data.to_array())
        elif isinstance(data, str):
            data_pointer = data.encode("utf-8")
        else:
            data_pointer = data
        h.update(data_pointer)
        digest = h.digest()
    return digest


def is_data_cached(data: Any, cache: Dict) -> Optional[int]:
    """
    Helper function to check if data is already in the cache dict

    Args:
        data (`Any`):
            The data to check in the cache.
        cache (`Dict`):
            The cache dictionary.

    Returns:
        data_id (`int`):
            The data id in the cache if the data is already in the cache, None otherwise.
    """
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    digest = _get_digest(data)

    if digest in cache:
        return cache[digest]
    return None


def cache_data(data: Any, data_id: int, cache: Dict) -> dict:
    """
    Helper function to add some data (numpy array, material, texture, anything hashable)
    in the cache dict as pointer to a provided data_id integer.

    Args:
        data (`Any`):
            The data to add to the cache.
        data_id (`int`):
            The data id to reference in the cache.
        cache (`Dict`):
            The cache dictionary.

    Returns:
        cache (`Dict`):
            The updated cache dictionary.
    """
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    digest = _get_digest(data)
    cache[digest] = data_id
    return cache


def add_data_to_gltf(
    new_data: Union[bytes, bytearray],
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """
    Add byte data to the buffer_data, create/add a new buffer view for it in the scene and
    return the index of the added buffer view

    Args:
        new_data (`bytes` or `bytearray`):
            The data to add to the buffer.
        gltf_model (`GLTFModel`):
            The gltf model to add the buffer view to.
        buffer_data (`bytearray`):
            The buffer data to add the data to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the buffer view to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        buffer_view_id (`int`):
            The id of the added buffer view.
    """
    cached_id = is_data_cached(data=new_data, cache=cache)
    if cached_id is not None:
        return cached_id

    # Pad the current buffer to a multiple of 4 bytes for GLTF alignment
    byte_offset = gl.padbytes(buffer_data, 4)

    # Pad new data to a multiple of 4 bytes as well
    byte_length = gl.padbytes(new_data, 4)

    # Add our binary data to the end of the buffer
    buffer_data.extend(new_data)

    # Create/add a new bufferView
    buffer_view = gl.BufferView(buffer=buffer_id, byteLength=byte_length, byteOffset=byte_offset, byteStride=None)
    gltf_model.bufferViews.append(buffer_view)
    buffer_view_id = len(gltf_model.bufferViews) - 1

    cache_data(data=new_data, data_id=buffer_view_id, cache=cache)
    return buffer_view_id


def add_numpy_to_gltf(
    np_array: np.ndarray,
    gltf_model: gl.GLTFModel,
    buffer_data: Union[bytearray, ByteString],
    normalized: bool = False,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """
    Create/add GLTF accessor and buffer view to the GLTF scene to store a numpy array and
    add the numpy array in the buffer_data.

    Args:
        np_array (`np.ndarray`):
            The numpy array to add to the buffer.
        gltf_model (`GLTFModel`):
            The gltf model to add the buffer view to.
        buffer_data (`bytearray`):
            The buffer data to add the data to.
        normalized (`bool`, *optional*, defaults to `False`):
            Whether the data is normalized.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the buffer view to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        accessor_id (`int`):
            The id of the added accessor.
    """

    cached_id = is_data_cached(data=np_array, cache=cache)
    if cached_id is not None:
        return cached_id

    component_type: gl.ComponentType = numpy_to_gltf_dtypes_mapping[np_array.dtype]
    accessor_type: gl.AccessorType = numpy_to_gltf_shapes_mapping[np_array.shape[1:]]

    if (
        accessor_type == gl.AccessorType.MAT2
        and component_type in [gl.ComponentType.BYTE, gl.ComponentType.UNSIGNED_BYTE]
    ) or (
        accessor_type == gl.AccessorType.MAT3
        and component_type
        in [
            gl.ComponentType.BYTE,
            gl.ComponentType.UNSIGNED_BYTE,
            gl.ComponentType.SHORT,
            gl.ComponentType.UNSIGNED_SHORT,
        ]
    ):
        raise NotImplementedError(
            "Column padding should be implemented in these cases."
            "Cf https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.html#data-alignment"
        )

    count: int = np_array.shape[0]
    max_value = np_array.max(axis=0).reshape(-1).tolist()
    min_value = np_array.min(axis=0).reshape(-1).tolist()

    new_data = np_array.tobytes()
    buffer_view_id = add_data_to_gltf(
        new_data=new_data, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
    )

    # Create and add a new Accessor
    accessor = gl.Accessor(
        bufferView=buffer_view_id,
        byteOffset=0,
        componentType=component_type.value,
        normalized=normalized,
        type=accessor_type.value,
        count=count,
        min=min_value,
        max=max_value,
        sparse=None,
    )
    gltf_model.accessors.append(accessor)
    accessor_id = len(gltf_model.accessors) - 1

    cache_data(data=np_array, data_id=accessor_id, cache=cache)

    return accessor_id


def add_texture_to_gltf(
    texture: pv.Texture,
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """
    Create/add GLTF accessor and buffer view to the GLTF scene to store a texture and
    add the texture in the buffer_data.

    Args:
        texture (`pv.Texture`):
            The texture to add to the buffer.
        gltf_model (`GLTFModel`):
            The gltf model to add the buffer view to.
        buffer_data (`bytearray`):
            The buffer data to add the data to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the buffer view to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        texture_id (`int`):
            The id of the added texture.
    """

    inp = texture.GetInput()  # Get a UniformGrid - safety check
    if not inp or not inp.GetPointData().GetScalars():
        raise NotImplementedError("Cannot cast texture")

    # Is the data already cached?
    cached_buffer = bytearray(memoryview(inp.GetPointData().GetScalars()).tobytes())
    cached_id = is_data_cached(data=cached_buffer, cache=cache)
    if cached_id is not None:
        return cached_id

    # This is some dark vtk magic inspired by
    # https://github.com/Kitware/VTK/blob/0718b3697bf4bd81c155a20d4f12bf5665ebe7c4/IO/Geometry/vtkGLTFWriter.cxx#L192
    from vtkmodules.vtkCommonExecutionModel import vtkTrivialProducer
    from vtkmodules.vtkIOImage import vtkPNGWriter

    triv = vtkTrivialProducer()
    triv.SetOutput(inp)  # To get an output port

    writer = vtkPNGWriter()
    writer.SetCompressionLevel(5)
    writer.SetInputConnection(triv.GetOutputPort())
    # writer.SetFileName('test.png')
    writer.WriteToMemoryOn()
    writer.Write()
    data = writer.GetResult()

    mem_view = memoryview(data)
    byte_array = bytearray(mem_view.tobytes())

    buffer_view_id = add_data_to_gltf(
        new_data=byte_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
    )

    gltf_image = gl.Image(bufferView=buffer_view_id, mimeType="image/png")
    gltf_model.images.append(gltf_image)
    image_id = len(gltf_model.images) - 1

    gltf_model.textures.append(gl.Texture(source=image_id))
    texture_id = len(gltf_model.textures) - 1

    cache_data(data=cached_buffer, data_id=texture_id, cache=cache)

    return texture_id


def add_material_to_gltf(
    material: Material,
    gltf_model: gl.GLTFModel,
    buffer_data: Union[bytearray, ByteString],
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """
    Add GLTF accessor and buffer view to the GLTF scene to store a Material and
    add the Material in the buffer_data.

    Args:
        material (`Material`):
            The material to add to the buffer.
        gltf_model (`GLTFModel`):
            The gltf model to add the buffer view to.
        buffer_data (`bytearray`):
            The buffer data to add the data to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the buffer view to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        material_id (`int`):
            The id of the added material.
    """

    cached_id = is_data_cached(data=material, cache=cache)
    if cached_id is not None:
        return cached_id

    # Store keys of the PBRMaterial which are images
    textures_to_add = {
        "baseColorTexture": material.base_color_texture,
        "emissiveTexture": material.emissive_texture,
        "normalTexture": material.normal_texture,
        "occlusionTexture": material.occlusion_texture,
        "metallicRoughnessTexture": material.metallic_roughness_texture,
    }

    textures_ids = {}
    for key, texture in textures_to_add.items():
        textures_ids[key] = None
        if texture is not None:
            texture_id = add_texture_to_gltf(
                texture=texture, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )
            textures_ids[key] = gl.TextureInfo(index=texture_id)

    pbr_metallic_roughness = gl.PBRMetallicRoughness(
        baseColorFactor=material.base_color,
        baseColorTexture=textures_ids["baseColorTexture"],
        metallicFactor=material.metallic_factor,
        roughnessFactor=material.roughness_factor,
        metallicRoughnessTexture=textures_ids["metallicRoughnessTexture"],
    )

    gl_material = gl.Material(
        name=material.name,
        pbrMetallicRoughness=pbr_metallic_roughness,
        normalTexture=textures_ids["normalTexture"],
        occlusionTexture=textures_ids["occlusionTexture"],
        emissiveTexture=textures_ids["emissiveTexture"],
        emissiveFactor=material.emissive_factor,
        alphaMode=material.alpha_mode,
        alphaCutoff=material.alpha_cutoff,
        doubleSided=material.double_sided,
    )

    # Add the new material
    gltf_model.materials.append(gl_material)
    material_id = len(gltf_model.materials) - 1

    cache_data(data=material, data_id=material_id, cache=cache)

    return material_id


def add_mesh_to_model(
    meshes: Union[pv.UnstructuredGrid, pv.MultiBlock],
    materials: Union[Material, None],
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """
    Add GLTF accessor and buffer view to the GLTF scene to store a mesh and
    add the mesh in the buffer_data.

    Args:
        meshes (`pyvista.UnstructuredGrid` or `pyvista.MultiBlock`):
            The mesh(es) to add to the buffer.
        materials (`Material` or `None`):
            The material(s) to add to the buffer.
        gltf_model (`GLTFModel`):
            The gltf model to add the buffer view to.
        buffer_data (`bytearray`):
            The buffer data to add the data to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the buffer view to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        mesh_id (`int`):
            The id of the added mesh.
    """
    if not isinstance(meshes, pv.MultiBlock):
        meshes = [meshes]
        materials = [materials]
    else:
        pass

    # handle case if Material is None
    if materials is None:
        materials = [materials]

    primitives = []

    for mesh, material in zip(meshes, materials):
        if mesh.n_verts == 0 and mesh.n_lines == 0 and mesh.n_faces == 0:
            raise NotImplementedError()

        # Store points in gltf
        np_array = mesh.points.astype(NP_FLOAT32)
        point_accessor = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )

        # Store vertex normals in gltf (TODO maybe not always necessary?)
        normal_accessor = None
        if mesh.active_normals is not None:
            np_array = mesh.active_normals.astype(NP_FLOAT32)
            normal_accessor = add_numpy_to_gltf(
                np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )

        # Store texture coord in gltf (TODO maybe not always necessary?)
        tcoord_accessor = None
        if mesh.active_t_coords is not None:
            np_array = mesh.active_t_coords.astype(NP_FLOAT32)
            tcoord_accessor = add_numpy_to_gltf(
                np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )

        if material is not None and isinstance(material, Material):
            # Add a material and/or texture if we want
            material_id = add_material_to_gltf(
                material=material, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )
        else:
            material_id = None

        attributes = gl.Attributes(POSITION=point_accessor, NORMAL=normal_accessor, TEXCOORD_0=tcoord_accessor)
        # attributes.COLOR_0 = vertex_accessor  # TODO Add back vertex color if we want to

        # Add verts as a Primitive if we have some
        if mesh.n_verts:
            primitive = gl.Primitive(mode=gl.PrimitiveMode.POINTS.value, attributes=attributes)
            # Stores and add indices (indices are written differently in gltf depending on the type
            # (POINTS, LINES, TRIANGLES))
            np_array = mesh.verts.copy().reshape((-1, 1)).astype(NP_UINT32)
            primitive.indices = add_numpy_to_gltf(
                np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )
            primitive.material = material_id
            primitives.append(primitive)

        # Add lines as a Primitive if we have some
        if mesh.n_lines:
            primitive = gl.Primitive(mode=gl.PrimitiveMode.LINES.value, attributes=attributes)
            # Stores and add indices (indices are written differently in gltf depending on the type
            # (POINTS, LINES, TRIANGLES))
            np_array = mesh.lines.copy().reshape((-1, 1)).astype(NP_UINT32)
            primitive.indices = add_numpy_to_gltf(
                np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )
            primitive.material = material_id
            primitives.append(primitive)

        # Add faces as a Primitive if we have some
        if mesh.n_faces:
            primitive = gl.Primitive(mode=gl.PrimitiveMode.TRIANGLES.value, attributes=attributes)
            # Stores and add indices (indices are written differently in gltf depending on the type
            # (POINTS, LINES, TRIANGLES))
            tri_mesh = mesh.triangulate()  # Triangulate the mesh (gltf can nly store triangulated meshes)
            np_array = (
                tri_mesh.faces.copy().reshape((-1, 4))[:, 1:].reshape(-1, 1).astype(NP_UINT32)
            )  # We drop the number of indices per face
            primitive.indices = add_numpy_to_gltf(
                np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
            )
            primitive.material = material_id
            primitives.append(primitive)

    # Create a final new mesh with all the primitives
    gltf_mesh = gl.Mesh(primitives=primitives)

    # If we have already created exactly the same mesh we avoid double storing
    cached_id = is_data_cached(data=gltf_mesh.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    gltf_model.meshes.append(gltf_mesh)
    mesh_id = len(gltf_model.meshes) - 1

    cache_data(data=gltf_mesh.to_json(), data_id=mesh_id, cache=cache)

    return mesh_id


def add_camera_to_model(
    camera: Camera, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
    """
    Add GLTF accessor and buffer view to the GLTF scene to store a camera and
    add the camera in the buffer_data.

    Args:
        camera (`Camera`):
            The camera to add to the GLTF scene.
        gltf_model (`GLTFModel`):
            The GLTF model to add the camera to.
        buffer_data (`ByteString`):
            The buffer data to add the camera to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the camera to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache to use to avoid double storing the same data.

    Returns:
        camera_id (`int`):
            The id of the added camera.

    """
    gl_camera = gl.Camera(
        type=camera.camera_type,
        width=camera.width,
        height=camera.height,
    )

    if camera.camera_type == "perspective":
        gl_camera.perspective = gl.PerspectiveCameraInfo(
            aspectRatio=camera.aspect_ratio, yfov=np.radians(camera.yfov), zfar=camera.zfar, znear=camera.znear
        )
    else:
        gl_camera.orthographic = gl.OrthographicCameraInfo(
            xmag=camera.xmag, ymag=camera.ymag, zfar=camera.zfar, znear=camera.znear
        )

    if camera.sensor_tag is not None:
        gl_camera.extras = {"sensor_tag": camera.sensor_tag}

    # If we have already created exactly the same camera we avoid double storing
    cached_id = is_data_cached(data=gl_camera.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new camera
    gltf_model.cameras.append(gl_camera)
    camera_id = len(gltf_model.cameras) - 1

    cache_data(data=gl_camera.to_json(), data_id=camera_id, cache=cache)

    return camera_id


def add_light_to_model(
    node: Light, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
    """
    Add GLTF accessor and buffer view to the GLTF scene to store a light and
    add the light in the buffer_data.

    Args:
        node (`Light`):
            The light to add to the GLTF scene.
        gltf_model (`GLTFModel`):
            The GLTF model to add the light to.
        buffer_data (`ByteString`):
            The buffer data to add the light to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the light to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache to use to avoid double storing the same data.

    Returns:
        light_id (`int`):
            The id of the added light.
    """
    light_type = node.light_type
    if light_type == "positional":
        if node.outer_cone_angle is None or node.outer_cone_angle > np.pi / 2:
            light_type = "point"
        else:
            light_type = "spot"

    light = gl.KHRLightsPunctualLight(type=light_type, color=node.color, intensity=node.intensity, range=node.range)

    if light_type == "spot":
        light.innerConeAngle = node.inner_cone_angle
        light.outerConeAngle = node.outer_cone_angle

    # If we have already created exactly the same light we avoid double storing
    cached_id = is_data_cached(data=light.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new light
    if gltf_model.extensions.KHR_lights_punctual is None:
        gltf_model.extensions.KHR_lights_punctual = gl.KHRLightsPunctual(lights=[light])
    else:
        gltf_model.extensions.KHR_lights_punctual.lights.append(light)
    light_id = len(gltf_model.extensions.KHR_lights_punctual.lights) - 1

    cache_data(data=light.to_json(), data_id=light_id, cache=cache)

    return light_id


def add_node_to_scene(
    node: "Asset",
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    gl_parent_node_id: Optional[int] = None,
    buffer_id: Optional[int] = 0,
    cache: Optional[Dict] = None,
) -> Set[str]:
    """
    Add a node to a scene.

    Args:
        node (`Asset`):
            The node to add to the GLTF scene.
        gltf_model (`GLTFModel`):
            The GLTF model to add the node to.
        buffer_data (`ByteString`):
            The buffer data to add the node to.
        gl_parent_node_id (`int`, *optional*, defaults to `None`):
            The parent node id to add the node to.
        buffer_id (`int`, *optional*, defaults to `0`):
            The buffer id to add the node to.
        cache (`Dict`, *optional*, defaults to `None`):
            The cache dictionary.

    Returns:
        extensions_used (`Set[str]`):
            The extensions used by the GLTF scene.
    """
    translation = list(node.position) if node.position is not None else None
    rotation = list(node.rotation) if node.rotation is not None else None
    scale = list(node.scaling) if node.scaling is not None else None

    if translation is None and rotation is None and scale is None and node.transformation_matrix is not None:
        # We transpose to get Column major format for gltf
        matrix = node.transformation_matrix.transpose().tolist() if node.transformation_matrix is not None else None
    else:
        matrix = None

    gl_node = gl.Node(
        name=node.name,
        translation=translation,
        rotation=rotation,
        scale=scale,
        matrix=matrix,
    )

    extensions = gl.Extensions()
    extras = dict()
    extension_used = set()

    if isinstance(node, Camera):
        gl_node.camera = add_camera_to_model(
            camera=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
    elif isinstance(node, Light):
        light_id = add_light_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.KHR_lights_punctual = gl.KHRLightsPunctual(light=light_id)
        extension_used.add("KHR_lights_punctual")

    elif isinstance(node, Object3D):
        # For Object3D and for Collider we can have a mesh
        gl_node.mesh = add_mesh_to_model(
            meshes=node.mesh,
            materials=getattr(node, "material", None),
            gltf_model=gltf_model,
            buffer_data=buffer_data,
            buffer_id=buffer_id,
            cache=cache,
        )
    else:
        for cls in GLTF_NODES_EXTENSION_CLASS:
            # One of our special type of nodes (RewardFunction, Sensors, Colliders, etc)
            if isinstance(node, cls):
                # For the colliders we add the physic material and mesh manually
                if isinstance(node, Collider):
                    material = getattr(node, "material", None)
                    if material is not None:
                        material_id = is_data_cached(data=material, cache=cache)
                        if material_id is None:
                            material_id = material.add_component_to_gltf_model(gltf_model.extensions)
                            cache_data(data=material.to_json(), data_id=material_id, cache=cache)
                        node.physic_material = material_id
                    else:
                        node.physic_material = None

                    if node.mesh is not None:
                        gl_node.mesh = add_mesh_to_model(
                            meshes=node.mesh,
                            materials=None,
                            gltf_model=gltf_model,
                            buffer_data=buffer_data,
                            buffer_id=buffer_id,
                            cache=cache,
                        )

                # If the special node is not cached
                # (here we test only the fields of the dataclass and thus must add te mesh manually above)
                object_id = is_data_cached(data=node.to_json(), cache=cache)
                if object_id is None:
                    object_id = node.add_component_to_gltf_model(gltf_model.extensions)
                    cache_data(data=node.to_json(), data_id=object_id, cache=cache)

                new_extension_used = node.add_component_to_gltf_node(
                    extensions, object_id=object_id, object_name=node.name
                )
                extension_used.add(new_extension_used)

    # Add all the automatic components of the node
    for component_name, component in node.named_components:
        # If we have already created exactly the same collider we avoid double storing
        object_id = is_data_cached(data=component.to_json(), cache=cache)
        if object_id is None:
            object_id = component.add_component_to_gltf_model(gltf_model.extensions)
            cache_data(data=component.to_json(), data_id=object_id, cache=cache)

        new_extension_used = component.add_component_to_gltf_node(
            extensions, object_id=object_id, object_name=component_name
        )
        extension_used.add(new_extension_used)

    # Store a couple of fields in the extras
    # We use the extras to avoid having extensions only for a few fields
    if getattr(node, "is_actor", False):
        extras["is_actor"] = node.is_actor

    # Add the extras to the node is anything in it
    if len(extras) > 0:
        gl_node.extras = extras

    # Add custom extensions, if any
    if node.extensions is not None and len(node.extensions) > 0:
        extensions.HF_custom = node.extensions
        extension_used.add("HF_custom")

    # Add the extensions to the node if anything not none
    if extension_used:
        gl_node.extensions = extensions

    # Add the new node
    gltf_model.nodes.append(gl_node)
    gl_node_id = len(gltf_model.nodes) - 1

    # List as a child in parent node in GLTF scene if not root node
    if gl_parent_node_id is not None:
        if gltf_model.nodes[gl_parent_node_id].children is None:
            gltf_model.nodes[gl_parent_node_id].children = [gl_node_id]
        else:
            gltf_model.nodes[gl_parent_node_id].children.append(gl_node_id)

    # Add the child nodes to the scene
    for child_node in node.tree_children:
        new_extensions = add_node_to_scene(
            node=child_node,
            gl_parent_node_id=gl_node_id,
            gltf_model=gltf_model,
            buffer_data=buffer_data,
            buffer_id=buffer_id,
            cache=cache,
        )
        extension_used.update(new_extensions)

    return extension_used


def tree_as_gltf(root_node: "Asset") -> gl.GLTF:
    """
    Return the tree of Assets as GLTF object.

    Args:
        root_node (`Asset`):
            The root node of the tree to export as glTF.

    Returns:
        gltf (`GLTF`):
            The glTF object.
    """
    buffer_data = bytearray()
    gltf_model = gl.GLTFModel(
        accessors=[],
        animations=[],
        asset=gl.Asset(version="2.0"),
        buffers=[],
        bufferViews=[],
        cameras=[],
        images=[],
        materials=[],
        meshes=[],
        nodes=[],
        samplers=[],
        scene=0,
        scenes=[gl.Scene(nodes=[0])],
        skins=[],
        textures=[],
        extensions=gl.Extensions(),
    )
    cache = {}  # A mapping for Mesh/material/Texture already added

    process_tree_before_gltf(root_node)

    # Add all the nodes and get back all the extensions used
    extension_used = add_node_to_scene(
        node=root_node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=0, cache=cache
    )

    # Add scene-level extensions - only config metadata for now
    config: Optional[Config] = getattr(root_node, "config", None)
    if config is not None:
        new_extension_used = config.add_component_to_gltf_scene(gltf_model.extensions)
        extension_used.add(new_extension_used)

    process_tree_after_gltf(root_node)

    # Update scene requirements with the GLTF extensions we need
    if extension_used:
        gltf_model.extensionsUsed = list(extension_used)

    resource = gl.FileResource("scene.bin", data=buffer_data)
    # TODO: refactor adding buffer
    buffer = gl.Buffer()
    buffer.byteLength = len(buffer_data)
    buffer.uri = "scene.bin"
    gltf_model.buffers.append(buffer)

    # TODO: refactor how empty properties are handled
    attributes = [a for a in dir(gltf_model) if not a.startswith("__") and isinstance(getattr(gltf_model, a), list)]
    for attribute in attributes:
        if len(getattr(gltf_model, attribute)) == 0:
            setattr(gltf_model, attribute, None)

    return gl.GLTF(model=gltf_model, resources=[resource])


def tree_as_glb_bytes(root_node: "Asset") -> bytes:
    """
    Return the tree of Assets as GLB bytes.

    Args:
        root_node (`Asset`):
            The root node of the tree to export as GLB bytes.

    Returns:
        glb_bytes (`bytes`):
            The glTF scene exported as GLB bytes.
    """
    gltf = tree_as_gltf(root_node=root_node)
    return gltf.as_glb_bytes()


def save_tree_to_gltf_file(file_path: str, root_node: "Asset") -> List[str]:
    """
    Save the tree in a GLTF file + additional (binary) resource files if it should be the case.
    Return the list of all the path to the saved files (glTF file + resource files)

    Args:
        file_path (`str`):
            The path to the file to save the scene to.
        root_node (`Asset`):
            The root node of the tree to export as glTF.

    Returns:
        file_paths (`List[str]`):
            The list of all the path to the saved files (glTF file + resource files)
    """
    gltf = tree_as_gltf(root_node=root_node)

    # For now let's convert all in GLTF with embedded resources
    for resource in gltf.resources:
        gltf.convert_to_base64_resource(resource)

    file_names = gltf.export_gltf(file_path)
    return file_names
