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
from typing import TYPE_CHECKING, Any, ByteString, Dict, List, Optional, Set

import numpy as np
import pyvista as pv



try:
    from gym import spaces
except ImportError:
    space = None

if TYPE_CHECKING:
    from ..rl import RlComponent, RewardFunction

from . import Asset, Camera, CameraSensor, Light, Material, Object3D, StateSensor
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


def _get_digest(data: Any) -> bytes:
    """Get a hash digest of the data"""
    if isinstance(data, Material):
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
    """Helper function to check if data (numpy arrray, material, texture, anything hashable) is already in the cache dict"""
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    digest = _get_digest(data)

    if digest in cache:
        return cache[digest]
    return None


def cache_data(data: Any, data_id: int, cache: Dict) -> dict:
    """Helper function to add some data (numpy arrray, material, texture, anything hashable) in the cache dict as pointer to a provided data_id integer"""
    if not isinstance(cache, dict):
        raise ValueError("Cache should be a dict")

    digest = _get_digest(data)

    cache[digest] = data_id

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
            aspectRatio=camera.aspect_ratio, yfov=np.radians(camera.yfov), zfar=camera.zfar, znear=camera.znear
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


def add_camera_sensor_to_model(
    camera_sensor: CameraSensor,
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:

    gl_camera_sensor = gl.HFCameraSensor(
        type=camera_sensor.camera_type, width=camera_sensor.width, height=camera_sensor.height
    )
    if camera_sensor.camera_type == "perspective":
        gl_camera_sensor.perspective = gl.PerspectiveCameraInfo(
            aspectRatio=camera_sensor.aspect_ratio,
            yfov=np.radians(camera_sensor.yfov),
            zfar=camera_sensor.zfar,
            znear=camera_sensor.znear,
        )
    else:
        gl_camera_sensor.orthographic = gl.OrthographicCameraInfo(
            xmag=camera_sensor.xmag, ymag=camera_sensor.ymag, zfar=camera_sensor.zfar, znear=camera_sensor.znear
        )

    # If we have already created exactly the same camera we avoid double storing
    cached_id = is_data_cached(data=gl_camera_sensor.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new camera sensor

    if gltf_model.extensions.HF_camera_sensors is None:
        gltf_model.extensions.HF_camera_sensors = gl.HFCameraSensors(camera_sensors=[gl_camera_sensor])
    else:
        gltf_model.extensions.HF_camera_sensors.camera_sensors.append(gl_camera_sensor)
    id = len(gltf_model.extensions.HF_camera_sensors.camera_sensors) - 1

    cache_data(data=gl_camera_sensor.to_json(), data_id=id, cache=cache)

    return id


def add_state_sensor_to_model(
    state_sensor: StateSensor,
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    buffer_id: int = 0,
    cache: Optional[Dict] = None,
) -> int:

    gl_state_sensor = gl.HFStateSensor(
        reference_entity_name=state_sensor.reference_entity.name,
        target_entity_name=state_sensor.target_entity.name,
        properties=state_sensor.properties,
    )

    # If we have already created exactly the same state sensor we avoid double storing
    cached_id = is_data_cached(data=gl_state_sensor.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new state sensor

    if gltf_model.extensions.HF_state_sensors is None:
        gltf_model.extensions.HF_state_sensors = gl.HFStateSensors(state_sensors=[gl_state_sensor])
    else:
        gltf_model.extensions.HF_state_sensors.state_sensors.append(gl_state_sensor)
    id = len(gltf_model.extensions.HF_state_sensors.state_sensors) - 1

    cache_data(data=gl_state_sensor.to_json(), data_id=id, cache=cache)

    return id


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


def add_rigidbody_to_model(
    node: Asset, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
    node_rb = node.physics_component
    rigidbody = gl.HFRigidbodiesRigidbody(
        mass=node_rb.mass,
        drag=node_rb.drag,
        angular_drag=node_rb.angular_drag,
        constraints=node_rb.constraints,
        use_gravity=node_rb.use_gravity,
        continuous=node_rb.continuous,
        kinematic=node_rb.kinematic,
    )

    # If we have already created exactly the same rigidbody we avoid double storing
    cached_id = is_data_cached(data=rigidbody.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new rigidbody
    if gltf_model.extensions.HF_rigidbodies is None:
        gltf_model.extensions.HF_rigidbodies = gl.HFRigidbodies(rigidbodies=[rigidbody])
    else:
        gltf_model.extensions.HF_rigidbodies.rigidbodies.append(rigidbody)
    rigidbody_id = len(gltf_model.extensions.HF_rigidbodies.rigidbodies) - 1

    cache_data(data=rigidbody.to_json(), data_id=rigidbody_id, cache=cache)

    return rigidbody_id


def get_gl_reward(reward) -> gl.HFRlAgentsReward:
    # If reward is none, which means that its parent is not a and / or / not reward function
    if reward is None:
        return None

    return gl.HFRlAgentsReward(
        type=reward.type,
        entity_a=reward.entity_a.name,
        entity_b=reward.entity_b.name,
        distance_metric=reward.distance_metric,
        scalar=reward.scalar,
        threshold=reward.threshold,
        is_terminal=reward.is_terminal,
        is_collectable=reward.is_collectable,
        trigger_once=reward.trigger_once,
        reward_function_a=get_gl_reward(reward.reward_function_a),
        reward_function_b=get_gl_reward(reward.reward_function_b),
    )


def add_rl_component_to_model(
    node: Asset, gltf_model: gl.GLTFModel, buffer_data: ByteString, buffer_id: int = 0, cache: Optional[Dict] = None
) -> int:
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
    gl_rewards = [get_gl_reward(reward) for reward in rewards]

    agent = gl.HFRlAgentsComponent(
        actions=gl_actions,
        sensorTypes=[type(asset).__name__ for asset in rl_component.sensors],
        sensorNames=[asset.name for asset in rl_component.sensors],
        rewards=gl_rewards,
    )

    # If we have already created exactly the same agent we avoid double storing
    cached_id = is_data_cached(data=agent.to_json(), cache=cache)
    if cached_id is not None:
        return cached_id

    # Add the new agent
    if gltf_model.extensions.HF_rl_agents is None:
        gltf_model.extensions.HF_rl_agents = gl.HFRlAgents(agents=[agent])
    else:
        gltf_model.extensions.HF_rl_agents.agents.append(agent)
    agent_id = len(gltf_model.extensions.HF_rl_agents.agents) - 1

    cache_data(data=agent.to_json(), data_id=agent_id, cache=cache)

    return agent_id


def add_node_to_scene(
    node: Asset,
    gltf_model: gl.GLTFModel,
    buffer_data: ByteString,
    gl_parent_node_id: Optional[int] = None,
    buffer_id: Optional[int] = 0,
    cache: Optional[Dict] = None,
) -> Set[str]:

    translation = node.position.tolist() if node.position is not None else None
    rotation = node.rotation.tolist() if node.rotation is not None else None
    scale = node.scaling.tolist() if node.scaling is not None else None

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
    extension_used = set()
    if isinstance(node, CameraSensor):
        sensor_id = add_camera_sensor_to_model(
            camera_sensor=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_camera_sensors = gl.HFCameraSensors(camera_sensor=sensor_id)
        extension_used.add("HF_camera_sensor")
    elif isinstance(node, StateSensor):
        sensor_id = add_state_sensor_to_model(
            state_sensor=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_state_sensors = gl.HFStateSensors(state_sensor=sensor_id)
        extension_used.add("HF_state_sensor")

    elif isinstance(node, Camera):
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
        agent_id = add_rl_component_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_rl_agents = gl.HFRlAgents(agent=agent_id)
        extension_used.add("HF_rl_agents")

    # Add Rigidbody if node has one
    if getattr(node, "physics_component", None) is not None:
        rigidbody_id = add_rigidbody_to_model(
            node=node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=buffer_id, cache=cache
        )
        extensions.HF_rigidbodies = gl.HFRigidbodies(rigidbody=rigidbody_id)
        extension_used.add("HF_rigidbodies")

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
    extension_used = add_node_to_scene(
        node=root_node, gltf_model=gltf_model, buffer_data=buffer_data, buffer_id=0, cache=cache
    )

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
