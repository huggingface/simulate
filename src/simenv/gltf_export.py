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
from copy import deepcopy
from io import BytesIO
from typing import ByteString, List, Optional, Set, Tuple

import numpy as np
import pyvista as pv

from simenv.gltflib.models.extensions.hf_collider import HF_Collider


try:
    import PIL.Image
except:
    pass

from . import gltflib as gl
from .assets import Asset, Camera, Capsule, Cube, Light, Material, Object3D, RLAgent, Sphere
from .gltflib.enums.collider_type import ColliderType
from .gltflib.utils import padbytes


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


def add_data_to_gltf(new_data: bytearray, gltf_model: gl.GLTFModel, buffer_data: bytearray, buffer_id: int = 0) -> int:
    """Add byte data to the buffer_data, create/add a new buffer view for it in the scene and return the index of the added buffer view"""
    # Pad the current buffer to a multiple of 4 bytes for GLTF alignement
    byte_offset = padbytes(buffer_data, 4)

    # Pad new data to a multiple of 4 bytes as well
    byte_length = padbytes(new_data, 4)

    # Add our binary data to the end of the buffer
    buffer_data.extend(new_data)

    # Create/add a new bufferView
    buffer_view = gl.BufferView(buffer=buffer_id, byteLength=byte_length, byteOffset=byte_offset, byteStride=None)
    gltf_model.bufferViews.append(buffer_view)
    buffer_view_id = len(gltf_model.bufferViews) - 1

    return buffer_view_id


def add_numpy_to_gltf(
    np_array: np.ndarray,
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    normalized: Optional[bool] = False,
    buffer_id: int = 0,
) -> int:
    """Create/add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""
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
        new_data=new_data, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
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

    return accessor_id


def add_image_to_gltf(image: "PIL.Image", gltf_model: gl.GLTFModel, buffer_data: bytearray, buffer_id: int = 0) -> int:
    """Create/add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""
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

    return texture_id


def add_material_to_gltf(
    material: Material,
    gltf_model: gl.GLTFModel,
    buffer_data: bytearray,
    buffer_id: int = 0,
) -> int:
    """Add GLTF accessor and bufferview to the GLTF scene to store a numpy array and add the numpy array in the buffer_data."""

    # Store keys of the PBRMaterial which are images
    images_to_add = {
        "baseColorTexture": material.baseColorTexture,
        "emissiveTexture": material.emissiveTexture,
        "normalTexture": material.normalTexture,
        "occlusionTexture": material.occlusionTexture,
        "metallicRoughnessTexture": material.metallicRoughnessTexture,
    }

    textures_ids = {}
    for key, image in images_to_add.items():
        textures_ids[key] = None
        if image is not None:
            texture_id = add_image_to_gltf(
                image=image, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
            )
            textures_ids[key] = gl.TextureInfo(index=texture_id)

    pbr_metallic_roughness = gl.PBRMetallicRoughness(
        baseColorFactor=material.baseColorFactor,
        baseColorTexture=textures_ids["baseColorTexture"],
        metallicFactor=material.metallicFactor,
        roughnessFactor=material.roughnessFactor,
        metallicRoughnessTexture=textures_ids["metallicRoughnessTexture"],
    )

    material = gl.Material(
        name=material.name,
        pbrMetallicRoughness=pbr_metallic_roughness,
        normalTexture=textures_ids["normalTexture"],
        occlusionTexture=textures_ids["occlusionTexture"],
        emissiveTexture=textures_ids["emissiveTexture"],
        emissiveFactor=material.emissiveFactor,
        alphaMode=material.alphaMode,
        alphaCutoff=material.alphaCutoff,
        doubleSided=material.doubleSided,
    )

    # Add the new material
    gltf_model.materials.append(material)
    material_id = len(gltf_model.materials) - 1

    return material_id


def add_mesh_to_model(node: Object3D, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0) -> int:
    mesh = node.mesh
    material = node.material
    if mesh.n_verts == 0 and mesh.n_lines == 0 and mesh.n_faces == 0:
        raise NotImplementedError()

    # Store points in gltf
    np_array = mesh.points.astype(NP_FLOAT32)
    point_accessor = add_numpy_to_gltf(
        np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
    )

    # Store vertex normals in gltf (TODO maybe not always necessary?)
    normal_accessor = None
    if mesh.active_normals is not None:
        np_array = mesh.active_normals.astype(NP_FLOAT32)
        normal_accessor = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )

    # Store texture coord in gltf (TODO maybe not always necessary?)
    tcoord_accessor = None
    if mesh.active_t_coords is not None:
        np_array = mesh.active_t_coords.astype(NP_FLOAT32)
        tcoord_accessor = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )

    if material is not None:
        # Add a material and/or texture if we want
        material_id = add_material_to_gltf(
            material=material, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
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
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )
        primitive.material = material_id
        primitives.append(primitive)

    # Add lines as a Primitive if we have some
    if mesh.n_lines:
        primitive = gl.Primitive(mode=gl.PrimitiveMode.LINES.value, attributes=attributes)
        # Stores and add indices (indices are written differently in gltf depending on the type (POINTS, LINES, TRIANGLES))
        np_array = mesh.lines.copy().reshape((-1, 1)).astype(NP_UINT32)
        primitive.indices = add_numpy_to_gltf(
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
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
            np_array=np_array, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )
        primitive.material = material_id
        primitives.append(primitive)

    # Add the new mesh
    gltf_mesh = gl.Mesh(primitives=primitives)
    gltf_model.meshes.append(gltf_mesh)
    mesh_id = len(gltf_model.meshes) - 1

    return mesh_id


def add_camera_to_model(camera: Camera, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0) -> int:
    gl_camera = gl.Camera(type=camera.camera_type)

    if camera.camera_type == "perspective":
        gl_camera.perspective = gl.PerspectiveCameraInfo(
            aspectRatio=camera.aspect_ratio, yfov=camera.yfov, zfar=camera.zfar, znear=camera.znear
        )
    else:
        gl_camera.orthographic = gl.OrthographicCameraInfo(
            xmag=camera.xmag, ymag=camera.ymag, zfar=camera.zfar, znear=camera.znear
        )

    # Add the new camera
    gltf_model.cameras.append(gl_camera)
    camera_id = len(gltf_model.cameras) - 1

    return camera_id


def add_light_to_model(node: Light, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0) -> int:
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

    # Add the new light
    if gltf_model.extensions.KHR_lights_punctual is None:
        gltf_model.extensions.KHR_lights_punctual = gl.KHRLightsPunctual(lights=[light])
    else:
        gltf_model.extensions.KHR_lights_punctual.lights.append(light)
    light_id = len(gltf_model.extensions.KHR_lights_punctual.lights) - 1

    return light_id


def add_agent_to_model(node: RLAgent, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0) -> int:

    # TODO: Split ActionDistribution and RewardFunction into separate GLTF extensions
    agent = gl.HF_RL_Agent(
        color=node.color,
        height=node.height,
        move_speed=node.move_speed,
        turn_speed=node.turn_speed,
        camera_width=node.camera_width,
        camera_height=node.camera_height,
        action_name=node.actions.name,
        action_dist=node.actions.dist,
        available_actions=node.actions.available_actions,
        reward_functions=[rf.function for rf in node.reward_functions],
        reward_entity1s=[rf.entity1 for rf in node.reward_functions],
        reward_entity2s=[rf.entity2 for rf in node.reward_functions],
        reward_distance_metrics=[rf.distance_metric for rf in node.reward_functions],
        reward_scalars=[rf.scalar for rf in node.reward_functions],
        reward_thresholds=[rf.threshold for rf in node.reward_functions],
        reward_is_terminals=[rf.is_terminal for rf in node.reward_functions],
    )

    if gltf_model.extensions.HF_RL_agents is None:
        gltf_model.extensions.HF_RL_agents = gl.HF_RL_Agents(agents=[agent])
    else:
        gltf_model.extensions.HF_RL_agents.agents.append(agent)
    agent_id = len(gltf_model.extensions.HF_RL_agents.agents) - 1

    return agent_id


def add_node_to_scene(
    node: Asset,
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    gl_parent_node_id: Optional[int] = None,
    buffer_id: Optional[int] = 0,
):
    gl_node = gl.Node(
        name=node.name,
        translation=node.position.tolist(),
        rotation=node.rotation.tolist(),
        scale=node.scaling.tolist(),
    )
    if isinstance(node, Camera):
        gl_node.camera = add_camera_to_model(
            camera=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )
    elif isinstance(node, Light):
        light_id = add_light_to_model(node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id)
        gl_node.extensions = gl.Extensions(KHR_lights_punctual=gl.KHRLightsPunctual(light=light_id))

    elif isinstance(node, RLAgent):
        agent_id = add_agent_to_model(node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id)
        gl_node.extensions = gl.Extensions(HF_RL_agents=gl.HF_RL_Agents(agent=agent_id))

    elif isinstance(node, Object3D):
        gl_node.mesh = add_mesh_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id
        )

    # Add collider if node has one
    if node.collider is not None:
        hf_collider = HF_Collider(
            type=node.collider.type,
            boundingBox=node.collider.bounding_box,
            mesh=node.collider.mesh,
            offset=node.collider.offset,
            intangible=node.collider.intangible,
        )
        if gl_node.extensions is None:
            gl_node.extensions = gl.Extensions(HF_collider=hf_collider)
        else:
            gl_node.extensions.HF_collider = hf_collider

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
        add_node_to_scene(
            node=child_node,
            gl_parent_node_id=gl_node_id,
            gltf_model=gltf_model,
            buffer_data=buffer_data,
            buffer_id=buffer_id,
        )

    return


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
    add_node_to_scene(node=root_node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=0)

    # Update scene requirements with the GLTF extensions we need
    if gltf_model.extensions.KHR_lights_punctual is not None:
        gltf_model.extensionsRequired = ["KHRLightsPunctual"]
        gltf_model.extensionsUsed = ["KHRLightsPunctual"]

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
