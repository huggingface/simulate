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
from dataclasses import asdict, fields
from io import BytesIO
from typing import TYPE_CHECKING, Any, ByteString, Dict, List, Optional

import numpy as np
import pyvista as pv
import xxhash


try:
    import PIL.Image
except ImportError:
    pass

try:
    from gym import spaces
except ImportError:
    space = None

if TYPE_CHECKING:
    from ..rl import RlComponent, RewardFunction

from . import Asset, Camera, Light, Material, Object3D
from . import gltflib as gl


# Conversion of Numnpy dtype and shapes in GLTF equivalents
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


def is_data_cached(data: Any, cache: Dict) -> Optional[int]:
    """Helper function to check if data (numpy arrray, material, texture, anything hashable) is already in the cache dict"""
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    if isinstance(data, Material):
        intdigest = hash(data)
    else:
        h = xxhash.xxh64()
        if isinstance(data, pv.Texture):
            data_pointer = np.ascontiguousarray(data.to_array())
        else:
            data_pointer = data
        h.update(data_pointer)
        intdigest = h.intdigest()

    if intdigest in cache:
        return cache[intdigest]
    return None


def cache_data(data: Any, data_id: int, cache: Dict) -> dict:
    """Helper function to add some data (numpy arrray, material, texture, anything hashable) in the cache dict as pointer to a provided data_id integer"""
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    if isinstance(data, Material):
        intdigest = hash(data)
    else:
        h = xxhash.xxh64()
        h.update(data)
        intdigest = h.intdigest()

    cache[intdigest] = data_id

    return cache


def add_data_to_gltf(
    new_data: bytearray,
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """Add byte data to the buffer_data, create/add a new buffer view for it in the scene and return the index of the added buffer view"""
    cached_id = is_data_cached(data=new_data, cache=cache)
    if cached_id is not None:
        return cached_id

    # Pad the current buffer to a multiple of 4 bytes for GLTF alignement
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
    buffer_data: bytearray,
    normalized: Optional[bool] = False,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """Create/add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""

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
    max = np_array.max(axis=0).reshape(-1).tolist()
    min = np_array.min(axis=0).reshape(-1).tolist()

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
        min=min,
        max=max,
        sparse=None,
    )
    gltf_model.accessors.append(accessor)
    accessor_id = len(gltf_model.accessors) - 1

    cache_data(data=np_array, data_id=accessor_id, cache=cache)

    return accessor_id


def add_image_to_gltf(
    image: "PIL.Image",
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """Create/add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""

    cached_id = is_data_cached(data=image, cache=cache)
    if cached_id is not None:
        return cached_id

    # don't re-encode JPEGs
    if image.format == "JPEG":
        # no need to mangle JPEGs
        save_as = "JPEG"
    else:
        # for everything else just use PNG
        save_as = "png"

    # get the image data into a bytes object
    with BytesIO() as f:
        image.save(f, format=save_as)
        f.seek(0)
        data = f.read()

    buffer_view_id = add_data_to_gltf(
        new_data=data, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
    )

    gltf_image = gl.Image(bufferView=buffer_view_id, mimeType="image/{}".format(save_as.lower()))
    gltf_model.images.append(gltf_image)
    image_id = len(gltf_model.images) - 1

    gltf_model.textures.append(gl.Texture(source=image_id))
    texture_id = len(gltf_model.textures) - 1

    cache_data(data=image, data_id=texture_id, cache=cache)

    return texture_id


def add_texture_to_gltf(
    texture: pv.Texture,
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """Create/add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""

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
    buffer_data: bytearray,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:
    """Add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""

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
    node: Object3D, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
    mesh = node.mesh
    material = node.material

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

    if material is not None:
        # Add a material and/or texture if we want
        material_id = add_material_to_gltf(
            material=material, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
    else:
        material_id = None

    attributes = gl.Attributes(POSITION=point_accessor, NORMAL=normal_accessor, TEXCOORD_0=tcoord_accessor)
    # attributes.COLOR_0 = vertex_accessor  # TODO Add back vertex color if we want to

    primitives = []

    # Add verts as a a Primitive if we have some
    if mesh.n_verts:
        primitive = gl.Primitive(mode=gl.PrimitiveMode.POINTS.value, attributes=attributes)
        # Stores and add indices (indices are written differently in gltf depending on the type (POINTS, LINES, TRIANGLES))
        np_array = mesh.verts.copy().reshape((-1, 1)).astype(NP_UINT32)
        primitive.indices = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        primitive.material = material_id
        primitives.append(primitive)

    # Add lines as a Primitive if we have some
    if mesh.n_lines:
        primitive = gl.Primitive(mode=gl.PrimitiveMode.LINES.value, attributes=attributes)
        # Stores and add indices (indices are written differently in gltf depending on the type (POINTS, LINES, TRIANGLES))
        np_array = mesh.lines.copy().reshape((-1, 1)).astype(NP_UINT32)
        primitive.indices = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        primitive.material = material_id
        primitives.append(primitive)

    # Add faces as a Primitive if we have some
    if mesh.n_faces:
        primitive = gl.Primitive(mode=gl.PrimitiveMode.TRIANGLES.value, attributes=attributes)
        # Stores and add indices (indices are written differently in gltf depending on the type (POINTS, LINES, TRIANGLES))
        tri_mesh = mesh.triangulate()  # Triangulate the mesh (gltf can nly store triangulated meshes)
        np_array = (
            tri_mesh.faces.copy().reshape((-1, 4))[:, 1:].reshape(-1, 1).astype(NP_UINT32)
        )  # We drop the number of indices per face
        primitive.indices = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        primitive.material = material_id
        primitives.append(primitive)

    # Create a final new mesh
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
    gl_camera = gl.Camera(type=camera.camera_type, width=camera.width, height=camera.height)

    if camera.camera_type == "perspective":
        gl_camera.perspective = gl.PerspectiveCameraInfo(
            aspectRatio=camera.aspect_ratio, yfov=camera.yfov, zfar=camera.zfar, znear=camera.znear
        )
    else:
        gl_camera.orthographic = gl.OrthographicCameraInfo(
            xmag=camera.xmag, ymag=camera.ymag, zfar=camera.zfar, znear=camera.znear
        )

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


def add_collider_to_model(
    node: Asset, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
    collider = gl.HFCollidersCollider(
        type=node.collider.type.value,
        boundingBox=node.collider.bounding_box,
        mesh=node.collider.mesh,
        offset=node.collider.offset,
        intangible=node.collider.intangible,
    )

    # If we have already created exactly the same collider we avoid double storing
    cached_id = is_data_cached(data=collider.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new collider
    if gltf_model.extensions.HF_colliders is None:
        gltf_model.extensions.HF_colliders = gl.HFColliders(colliders=[collider])
    else:
        gltf_model.extensions.HF_colliders.colliders.append(collider)
    collider_id = len(gltf_model.extensions.HF_colliders.colliders) - 1

    cache_data(data=collider.to_json(), data_id=collider_id, cache=cache)

    return collider_id


def add_rl_component_to_model(
    node: Asset, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> gl.HFRlAgentsComponent:
    rl_component: "RlComponent" = node.rl_component

    actions = rl_component.actions
    actions_type = actions.__class__.__name__
    if actions_type not in ["Discrete", "Box", "MappedDiscrete", "MappedBox"]:
        raise ValueError(f"Unsupported action space type: {actions_type}")

    gl_actions = gl.HFRlAgentsActions(
        type=actions_type,
        n=actions.n if "Discrete" in actions_type else None,
        low=actions.low if "Box" in actions_type else None,
        high=actions.high if "Box" in actions_type else None,
        shape=actions.shape if "Box" in actions_type else None,
        dtype=actions.dtype if "Box" in actions_type else None,
    )

    if "Mapped" in actions_type:
        gl_actions.physics = [phys.value for phys in actions.physics]
        gl_actions.clip_high = actions.clip_high
        gl_actions.clip_low = actions.clip_low
        gl_actions.amplitudes = actions.amplitudes if actions_type == "MappedDiscrete" else None
        gl_actions.scaling = actions.scaling if actions_type == "MappedBox" else None
        gl_actions.offset = actions.offset if actions_type == "MappedBox" else None

    rewards: "List[RewardFunction]" = rl_component.rewards
    gl_rewards = [
        gl.HFRlAgentsReward(
            type=reward.type,
            entity_a=reward.entity_a.name,
            entity_b=reward.entity_b.name,
            distance_metric=reward.distance_metric,
            scalar=reward.scalar,
            threshold=reward.threshold,
            is_terminal=reward.is_terminal,
            is_collectable=reward.is_collectable,
        )
        for reward in rewards
    ]

    gl_rl_component = gl.HFRlAgentsComponent(
        actions=gl_actions,
        observations=[asset.name for asset in rl_component.observations],
        rewards=gl_rewards,
    )
    return gl_rl_component


def add_node_to_scene(
    node: Asset,
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    gl_parent_node_id: Optional[int] = None,
    buffer_id: Optional[int] = 0,
    cache: Optional[Dict] = None,
) -> set[str]:
    gl_node = gl.Node(
        name=node.name,
        translation=node.position.tolist(),
        rotation=node.rotation.tolist(),
        scale=node.scaling.tolist(),
    )
    extensions = gl.Extensions()
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
        gl_node.mesh = add_mesh_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )

    # Add RL component if node has one
    if getattr(node, "rl_component", None) is not None:
        rl_component = add_rl_component_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_rl_agents = rl_component
        extension_used.add("HF_rl_agents")

    # Add collider if node has one
    if getattr(node, "collider", None) is not None:
        collider_id = add_collider_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_colliders = gl.HFColliders(collider=collider_id)
        extension_used.add("HF_colliders")

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


def tree_as_gltf(root_node: Asset) -> gl.GLTF:
    """Return the tree of Assets as GLTF object."""
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
    extension_used = add_node_to_scene(node=root_node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=0, cache=cache)

    # Update scene requirements with the GLTF extensions we need
    if gltf_model.extensions.KHR_lights_punctual is not None:
        # gltf_model.extensionsRequired = ["KHRLightsPunctual"]
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


def tree_as_glb_bytes(root_node: Asset) -> bytes:
    """Return the tree of Assets as GLB bytes."""
    gltf = tree_as_gltf(root_node=root_node)
    return gltf.as_glb_bytes()


def save_tree_to_gltf_file(file_path: str, root_node: Asset) -> List[str]:
    """Save the tree in a GLTF file + additional (binary) ressource files if if shoulf be the case.
    Return the list of all the path to the saved files (glTF file + ressource files)
    """
    gltf = tree_as_gltf(root_node=root_node)

    # For now let's convert all in GLTF with embedded ressources
    for ressource in gltf.resources:
        gltf.convert_to_base64_resource(ressource)

    file_names = gltf.export_gltf(file_path)
    return file_names
