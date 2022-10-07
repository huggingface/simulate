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
import os
import tempfile
from typing import ByteString, List, Optional, Union

import numpy as np
import PIL.Image
import pyvista as pv
from huggingface_hub import hf_hub_download

from . import Asset, Camera, Light, Material, Object3D
from .gltf_extension import GLTF_EXTENSIONS_REGISTER, GLTF_NODES_EXTENSION_CLASS, process_tree_after_gltf
from .gltflib import GLTF, Base64Resource, FileResource, TextureInfo
from .gltflib.enums import AccessorType, ComponentType


UNSUPPORTED_REQUIRED_EXTENSIONS = ["KHR_draco_mesh_compression"]


# TODO remove this GLTFReader once the new version of pyvista is released 0.34+ (included in it)
class GLTFReader(pv.utilities.reader.BaseReader):
    """GLTFeader for .gltf and .glb files.

    Examples:
    ```python
    reader = GLTFReader(filename)
    mesh = reader.read()  # A MultiBlock reproducing the hierarchy of Nodes in the GLTF file
    ```
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
    """
    Get a `ByteString` of the data stored in a GLTF buffer view.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        buffer_view_id (`int`):
            The id of the buffer view to extract.

    Returns:
        data (`ByteString`):
            The data stored in the buffer view.
    """
    gltf_model = gltf_scene.model

    buffer_view = gltf_model.bufferViews[buffer_view_id]
    buffer = gltf_model.buffers[buffer_view.buffer]
    resource = gltf_scene.get_resource(buffer.uri)
    if isinstance(resource, FileResource) and not resource.loaded:
        resource.load()

    byte_offset = buffer_view.byteOffset
    length = buffer_view.byteLength
    data = resource.data[byte_offset : byte_offset + length]

    return data


# TODO we can probably remove a lot of gltf method since we now have them supported through pyvista
# Still keeping them if we want to support our own collision shape and maybe complex operations
# To be cleaned up at the end
def get_image_as_bytes(gltf_scene: GLTF, image_id: int) -> ByteString:
    """
    Get a ByteString of the data stored in a GLTF image.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        image_id (`int`):
            The id of the image to extract.

    Returns:
        data (`ByteString`):
            The data stored in the image.
    """
    gltf_model = gltf_scene.model

    image = gltf_model.images[image_id]
    if image.bufferView is not None:
        return get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=image.bufferView)

    resource = gltf_scene.get_resource(image.uri)
    if not resource.loaded:
        resource.load()

    return resource.data


def get_accessor_as_numpy(gltf_scene: GLTF, accessor_id: int) -> np.ndarray:
    """
    Get a numpy array of the data stored in a GLTF accessor.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        accessor_id (`int`):
            The id of the accessor to extract.

    Returns:
        data (`np.ndarray`):
            The data stored in the accessor.
    """
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


def get_texture_as_pillow(gltf_scene: GLTF, texture_info: Optional[TextureInfo]) -> Optional[PIL.Image.Image]:
    """
    Get a Pillow image of the data stored in a GLTF texture.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        texture_info (`gltflib.TextureInfo`):
            The texture info to extract.

    Returns:
        image (`PIL.Image.Image`):
            The image stored in the texture.
    """
    if texture_info is None:
        return None

    gltf_textures = gltf_scene.model.textures
    gltf_images = gltf_scene.model.images
    # gltf_samplers = gltf_scene.model.samplers

    gltf_texture = gltf_textures[texture_info.index]
    gltf_image = gltf_images[gltf_texture.source]

    if gltf_image.bufferView is not None:
        data = get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=gltf_image.bufferView)
    else:
        resource = gltf_scene.get_resource(gltf_image.uri)
        if not resource.loaded:
            resource.load()
        data = resource.data

    image = PIL.Image.open(io.BytesIO(data))  # TODO check all this image stuff

    return image


def get_texture_as_pyvista(gltf_scene: GLTF, texture_info: Optional[TextureInfo]) -> Optional[pv.Texture]:
    """
    Get a PyVista texture of the data stored in a GLTF texture.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        texture_info (`gltflib.TextureInfo`):
            The texture info to extract.

    Returns:
        texture (`pyvista.Texture`):
            The texture stored in the texture.
    """
    if texture_info is None:
        return None

    gltf_textures = gltf_scene.model.textures
    gltf_images = gltf_scene.model.images
    # gltf_samplers = gltf_scene.model.samplers

    gltf_texture = gltf_textures[texture_info.index]
    gltf_image = gltf_images[gltf_texture.source]

    if gltf_image.bufferView is not None:
        # Temporarily store the image for loading with vtk
        buffer_bytes = get_buffer_as_bytes(gltf_scene=gltf_scene, buffer_view_id=gltf_image.bufferView)
        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = gltf_image.mimeType.replace("/", ".")  # Will convert mimeType 'image/png' in 'image.png'
            filepath = os.path.join(tmpdirname, filename)
            with open(filepath, "wb") as file:
                file.write(bytearray(buffer_bytes))
            texture = pv.read_texture(filepath)
    else:
        resource = gltf_scene.get_resource(gltf_image.uri)
        if isinstance(resource, Base64Resource):
            image = PIL.Image.open(io.BytesIO(resource.data))
            texture = pv.numpy_to_texture(np.array(image))
        else:
            texture = pv.read_texture(resource.fullpath)

    return texture


# Build a tree of simulate nodes from a GLTF object
def build_node_tree(
    gltf_scene: GLTF,
    pyvista_meshes: Union[np.ndarray, pv.MultiBlock],
    gltf_node_id: int,
    parent: Optional["Asset"] = None,
) -> List:
    """
    Build the node tree of simulate objects from the GLTF scene.

    Args:
        gltf_scene (`gltflib.GLTF`):
            The GLTF scene.
        pyvista_meshes (`pyvista.MultiBlock`):
            The pyvista meshes of the GLTF scene.
        gltf_node_id (`int`):
            The id of the GLTF node to build the tree from.
        parent (`simulate.Asset`):
            The parent of the node to build the tree from.

    Returns:
        nodes (`List[Asset]`):
            The list of nodes in the built tree.
    """
    gltf_model = gltf_scene.model
    gltf_node = gltf_model.nodes[gltf_node_id]
    common_kwargs = {
        "name": gltf_node.name,
        "position": gltf_node.translation,
        "rotation": gltf_node.rotation,
        "scaling": gltf_node.scale,
        "parent": parent,
    }
    if gltf_node.matrix is not None:
        mat = np.array(gltf_node.matrix).reshape(4, 4, order="F")
        common_kwargs["transformation_matrix"] = mat

    # Load the extensions
    if gltf_node.extensions is not None:
        for (extension_name, _, _) in GLTF_EXTENSIONS_REGISTER:
            node_extension = getattr(gltf_node.extensions, extension_name, None)
            if node_extension is not None:
                # We have either a special type of node (Reward, Sensor, Colliders)
                # Or a special type of components (added to a node)
                object_id = node_extension.object_id
                component_name = node_extension.name
                model_extension = getattr(gltf_model.extensions, extension_name, None)
                component = model_extension.objects[
                    object_id
                ].gltf_copy()  # Our GltfExtension mixing have a copy method

                # Is it a node or component
                if type(component) in GLTF_NODES_EXTENSION_CLASS:
                    common_kwargs["cls"] = component  # node
                else:
                    common_kwargs[component_name] = component  # component

    # Add material to collider
    gltf_collider = None
    if gltf_node.extensions is not None and gltf_node.extensions.HF_colliders is not None:
        gltf_collider = common_kwargs["cls"]
        material_id = gltf_collider.physic_material
        if material_id is not None:
            material = gltf_model.extensions.HF_physic_materials.objects[material_id]
            common_kwargs["material"] = material
            gltf_collider.physic_material = None

    # Create the various type of objects
    # Is it a camera
    if gltf_node.camera is not None:
        # Let's add a Camera
        gltf_camera = gltf_model.cameras[gltf_node.camera]
        camera_type = gltf_camera.type

        scene_node = Camera(
            aspect_ratio=gltf_camera.perspective.aspectRatio if camera_type == "perspective" else None,
            yfov=np.degrees(gltf_camera.perspective.yfov) if camera_type == "perspective" else None,
            zfar=gltf_camera.perspective.zfar if camera_type == "perspective" else gltf_camera.orthographic.zfar,
            znear=gltf_camera.perspective.znear if camera_type == "perspective" else gltf_camera.orthographic.znear,
            camera_type=camera_type,
            xmag=gltf_camera.orthographic.xmag if camera_type == "orthographic" else None,
            ymag=gltf_camera.orthographic.ymag if camera_type == "orthographic" else None,
            **common_kwargs,
        )
    # It is a light
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
                f"Unrecognized GLTF file light type: {gltf_light.type}, "
                f"please check that the file is conform with the KHR_lights_punctual specifications"
            )
    # Is it an Object3D
    elif gltf_node.mesh is not None:
        # Let's add a mesh
        gltf_mesh = gltf_model.meshes[gltf_node.mesh]
        primitives = gltf_mesh.primitives
        common_kwargs["with_rigid_body"] = False
        common_kwargs["with_articulation_body"] = False
        if len(primitives) > 1:
            mesh = pyvista_meshes[f"Mesh_{gltf_node.mesh}"]  # A pv.MultiBlock
        else:
            mesh = pyvista_meshes[f"Mesh_{gltf_node.mesh}"][0]  # A pv.PolyData

        common_kwargs["mesh"] = mesh

        if gltf_collider is None:
            material_ids = [p.material for p in primitives]
            scene_material = []
            for material_id in material_ids:
                if material_id is not None:
                    mat = gltf_model.materials[material_id]
                    pbr = mat.pbrMetallicRoughness

                    scene_material.append(
                        Material(
                            name=mat.name,
                            base_color=pbr.baseColorFactor,
                            base_color_texture=get_texture_as_pyvista(gltf_scene, pbr.baseColorTexture),
                            metallic_factor=pbr.metallicFactor,
                            metallic_roughness_texture=get_texture_as_pyvista(
                                gltf_scene, pbr.metallicRoughnessTexture
                            ),
                            normal_texture=get_texture_as_pyvista(gltf_scene, mat.normalTexture),
                            occlusion_texture=get_texture_as_pyvista(gltf_scene, mat.occlusionTexture),
                            emissive_factor=mat.emissiveFactor,
                            emissive_texture=get_texture_as_pyvista(gltf_scene, mat.emissiveTexture),
                            alpha_mode=mat.alphaMode,
                            alpha_cutoff=mat.alphaCutoff,
                        )
                    )
                else:
                    scene_material.append(Material())
            if len(scene_material) == 1:
                scene_material = scene_material[0]
            common_kwargs["material"] = scene_material

        if gltf_collider is not None:
            scene_node = gltf_collider
            for key, value in common_kwargs.items():
                # These two are different when set after creation
                if key == "parent":
                    key = "tree_parent"
                if key == "children":
                    key = "tree_children"
                setattr(scene_node, key, value)
        else:
            scene_node = Object3D(**common_kwargs)
    else:
        # We now have either an empty node with a transform or one of our custom nodes without meshes
        # (reward function, sensors, etc)
        if "cls" in common_kwargs:
            # We have a custom node type (reward function, sensors, etc)
            scene_node = common_kwargs.pop("cls")
            for key, value in common_kwargs.items():
                # These two are different when set after creation
                if key == "parent":
                    key = "tree_parent"
                if key == "children":
                    key = "tree_children"
                setattr(scene_node, key, value)
        else:
            scene_node = Asset(**common_kwargs)

    # Check if we have some extras fields
    if isinstance(gltf_node.extras, dict):
        if "sensor_tag" in gltf_node.extras:
            scene_node.sensor_tag = gltf_node.extras["sensor_tag"]
        if "is_actor" in gltf_node.extras:
            scene_node.is_actor = gltf_node.extras["is_actor"]

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


def load_gltf_as_tree(
    file_path: str,
    file_type: Optional[str] = None,
    repo_id: Optional[str] = None,
    subfolder: Optional[str] = None,
    revision: Optional[str] = None,
) -> Union[List[List], List["Asset"]]:
    """
    Loading function to create a tree of asset nodes from a GLTF file.
    Return a list of the main nodes in the GLTF files (often only one main node).
    The tree can be walked from the main nodes.

    Args:
        file_path (`str`):
            Path to the GLTF file
        file_type (`str`, *optional*, defaults to `None`):
            Type of the file to load.
        repo_id (`str`, *optional*, defaults to `None`):
            The id of the repo to load the file from.
            If `None`, the file will be loaded from the local file system.
        subfolder (`str`, *optional*, defaults to `None`):
            The subfolder of the repo to load the file from.
            If `None`, the file will be loaded from the root of the repo.
        revision (`str`, *optional*, defaults to `None`):
            The revision of the repo to load the file from.
            If `None`, the file will be loaded from the latest revision of the repo.

    Returns:
        nodes (`List[Asset`):
            The list of the main nodes in the GLTF files.
    """
    gltf_scene = GLTF.load(file_path)  # We load the other nodes (camera, lights, our extensions) ourselves

    # Let's download all the other needed resources
    if repo_id is not None:
        updated_resources = []
        for resource in gltf_scene.resources:
            if isinstance(resource, FileResource):
                local_file = hf_hub_download(
                    repo_id=repo_id,
                    filename=resource.filename,
                    subfolder=subfolder,
                    revision=revision,
                    repo_type="space",
                )
                basepath, basename = os.path.split(local_file)
                former_file_name_and_uri = resource.filename
                former_basename = os.path.basename(former_file_name_and_uri)
                if former_basename != basename:
                    raise ValueError(f"Hub file {basename} not matching expected resource filename {former_basename}")
                # We need to keep former_file_name_and_uri in the resource
                # because it's the uri used everywhere in the glTF file
                new_resource = FileResource(former_file_name_and_uri, basepath=basepath, mimetype=resource.mimetype)
                updated_resources.append(new_resource)
            else:
                updated_resources.append(resource)

        gltf_scene.resources = updated_resources

    gltf_model = gltf_scene.model

    if gltf_model.extensionsRequired is not None and gltf_model.extensionsRequired:
        for extension_required in gltf_model.extensionsRequired:
            # Sanity check of the required extension before running pyvista glTF reader
            # because it can segfault on some unsupported extensions.
            if extension_required in UNSUPPORTED_REQUIRED_EXTENSIONS:
                raise ValueError(
                    f"The glTF extension '{extension_required}' "
                    f"is required to load this scene but is not currently supported."
                )

    pyvista_reader = GLTFReader(
        file_path
    )  # We load the mesh already converted by pyvista/vtk instead of decoding our self
    pyvista_reader.reader.ApplyDeformationsToGeometryOff()  # We don't want to apply the transforms to the various nodes
    pyvista_meshes = pyvista_reader.read()
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
    for node in main_nodes:
        process_tree_after_gltf(node)

    return main_nodes
