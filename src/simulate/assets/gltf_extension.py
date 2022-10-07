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
""" Store a python dataclass as a glTF extension."""
import copy
from dataclasses import field, fields, is_dataclass, make_dataclass
from typing import TYPE_CHECKING, Any, List, Optional, Union

from dataclasses_json import DataClassJsonMixin, dataclass_json


if TYPE_CHECKING:
    from .asset import Asset

# We use this to define all the extension fields to have in the extension
GLTF_EXTENSIONS_REGISTER = []

# We use this to define all the scene level class in our scene which are defined as GLTF extensions
GLTF_SCENE_EXTENSION_CLASS = []

# We use this to define all the nodes class in our scene which are defined as GLTF extensions
GLTF_NODES_EXTENSION_CLASS = []

# We use this to define all the component class in our scene which are defined as GLTF extensions
GLTF_COMPONENTS_EXTENSION_CLASS = []


class GltfExtensionMixin(DataClassJsonMixin):
    """
    A Mixin class to extend a python dataclass to be a glTF extension.

    Requirements:
        - The extended python class must be a dataclass.
        - The attributes of the class must be
            * either JSON serializable, or
            * an Asset object to which the type should then be Union[str, Any]
              (converted in a string with the node name while saving to glTF and
               decoded to a pointer to the asset object while loading from glTF).

    Args:
        gltf_extension_name (`str`):
            The name of the glTF extension.
        object_type (`str`):
            Either "node" is the object is a node, or "component" if the object is a component (attached to a node)

    Examples:
    ```python
    class MyGltfExtension(GltfExtensionMixin,
                          gltf_extension_name="my_extension",
                          object_type="node"):
    ```
    """

    def __init_subclass__(cls, gltf_extension_name: str, object_type: str, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if not gltf_extension_name:
            raise ValueError("A glTF extension name must be provided.")
        if object_type not in ["scene", "node", "component"]:
            raise ValueError("The type of the object must be one of 'scene', 'node' or 'component'.")

        cls._gltf_extension_name = gltf_extension_name

        if object_type == "scene":
            gltf_extension_cls = cls  # We directly use the dataclass as the glTF extension
        elif object_type == "node":
            gltf_extension_cls = dataclass_json(
                make_dataclass(
                    gltf_extension_name,
                    [
                        ("objects", Optional[List[cls]], field(default=None)),
                        ("object_id", Optional[int], field(default=None)),
                        ("name", Optional[str], field(default=None)),
                    ],
                )
            )
        elif object_type == "component":
            gltf_extension_cls = dataclass_json(
                make_dataclass(
                    gltf_extension_name,
                    [
                        (
                            "objects",
                            Optional[List[cls]],
                            field(default=None),
                        ),  # TODO change this to "components" at some point
                        ("object_id", Optional[int], field(default=None)),
                        ("name", Optional[str], field(default=None)),
                    ],
                )
            )
        else:
            gltf_extension_cls = None

        cls._gltf_extension_cls = gltf_extension_cls

        # register the component to the glTF model extensions
        for (ext_name, _, _) in GLTF_EXTENSIONS_REGISTER:
            if ext_name == gltf_extension_name:
                raise ValueError(f"The glTF extension {gltf_extension_name} is already registered.")
        GLTF_EXTENSIONS_REGISTER.append((gltf_extension_name, Optional[cls._gltf_extension_cls], field(default=None)))

        if object_type == "scene":
            GLTF_SCENE_EXTENSION_CLASS.append(cls)
        elif object_type == "node":
            GLTF_NODES_EXTENSION_CLASS.append(cls)
        elif object_type == "component":
            GLTF_COMPONENTS_EXTENSION_CLASS.append(cls)
        else:
            raise ValueError(f"The object type {object_type} is not supported.")

    def gltf_copy(self) -> "GltfExtensionMixin":
        """
        Create a deep copy of the object with a deep copy of only the dataclass fields.

        In several cases we are modifying this asset and want to create picklable copies
        (e.g. at importation from GLTF or during the GLTF conversion to replace node pointers with string names).

        We then want to deep copy only the fields of the dataclass, thus we don't
        use copy.deepcopy since some other properties (renderer, etc.) are not picklable.

        Returns:
            copy (`GltfExtensionMixin`):
                A deep copy of the object with a deep copy of only the dataclass fields.
        """
        self_dict = {f.name: copy.deepcopy(getattr(self, f.name)) for f in fields(self)}
        copy_self = type(self)(**self_dict)
        return copy_self

    def add_component_to_gltf_scene(self, gltf_model_extensions) -> str:
        """
        Add a scene level object to a glTF scene (e.g. config).
        Only one object of each such type can be added to a scene.

        TODO: Complete typing for gltf_model_extensions
        Args:
            gltf_model_extensions ():
                The glTF model extensions.

        Returns:
            name (`str`):
                The name of the glTF extension.
        """
        copy_self = self.gltf_copy()  # Create a deep copy of the object keeping only the fields

        if getattr(gltf_model_extensions, self._gltf_extension_name, None) is None:
            if not hasattr(gltf_model_extensions, self._gltf_extension_name):
                raise ValueError(f"The glTF model extensions does not have the {self._gltf_extension_name} extension.")
            setattr(gltf_model_extensions, self._gltf_extension_name, copy_self)
        else:
            raise ValueError(f"The glTF model extensions already has the {self._gltf_extension_name} extension.")
        return self._gltf_extension_name

    def add_component_to_gltf_model(self, gltf_model_extensions) -> int:
        """
        Add a component to a glTF model.

        TODO: Complete typing for gltf_model_extensions
        Args:
            gltf_model_extensions ():
                The glTF model extensions.

        Returns:
            id (`int`):
                The index of the component in the glTF model extensions.
        """
        copy_self = self.gltf_copy()  # Create a deep copy of the object keeping only the fields

        if getattr(gltf_model_extensions, self._gltf_extension_name, None) is None:
            objects = [copy_self]
            # Create a component class to store our component
            new_extension_component_cls = self._gltf_extension_cls(objects=objects)
            if not hasattr(gltf_model_extensions, self._gltf_extension_name):
                raise ValueError(f"The glTF model extensions does not have the {self._gltf_extension_name} extension.")
            setattr(gltf_model_extensions, self._gltf_extension_name, new_extension_component_cls)
        else:
            objects = getattr(getattr(gltf_model_extensions, self._gltf_extension_name), "objects")
            objects.append(copy_self)
        object_id = len(objects) - 1
        return object_id

    def add_component_to_gltf_node(self, gltf_node_extensions, object_id: int, object_name: str) -> str:
        """
        Add a component to a glTF node.

        TODO: Complete typing for gltf_node_extensions
        Args:
            gltf_node_extensions ():
                The glTF node extensions dataclass_json.
            object_id (`int`):
                The index of the component in the glTF model extensions.
            object_name (`str`):
                The name of the component in the glTF model extensions.

        Returns:
            name (`str`):
                The name of the glTF node extensions.
        """
        node_extension_cls = self._gltf_extension_cls(object_id=object_id, name=object_name)
        if not hasattr(gltf_node_extensions, self._gltf_extension_name):
            raise ValueError(f"The glTF node extensions does not have the {self._gltf_extension_name} extension.")
        setattr(gltf_node_extensions, self._gltf_extension_name, node_extension_cls)
        return self._gltf_extension_name


def _process_dataclass_after(obj_dataclass, node: "Asset", object_name: Optional[str] = None):
    """
    Process the dataclass after the deserialization.

    TODO: Complete typing for obj_dataclass
    Args:
        obj_dataclass ():
            The dataclass to process.
        node (`Asset`):
            The node to which the dataclass belongs.
        object_name (`str`, *optional*, defaults to `None`):
            The name of the object.
    """
    for f in fields(obj_dataclass):
        value = getattr(obj_dataclass, f.name)
        type_ = f.type
        # If the attribute of the component has the right type:
        # "Any" or "Optional[Any]" with a name attribute in the pointed object
        # Then we assume it's a node in the tree + we replace a name of a pointed node by a direct pointer to the node
        # We check the named node exist for safety
        # Note that this only investigate the fields of the dataclass
        # and thus not the "children" or "parent" attribute of an Asset, thus keeping the tree in good shape
        if type_ == Any or type_ == Optional[Any]:
            if isinstance(value, str):
                node_pointer = node.get_node(value)
                if node_pointer is None:
                    raise ValueError(
                        f"The field {f.name} '{'of component' + object_name if object_name is not None else ''}'"
                        f" of node '{node.name}' has type 'Any' "
                        f"point to a second asset called '{value}' but this second asset cannot be found "
                        f"in the asset tree. Please check the name of the second asset is correct "
                        f"and the second asset is present in the scene or "
                        f"change the type of the component to be a string."
                    )
                setattr(obj_dataclass, f.name, node_pointer)  # We convert it in the node pointer
        # Recursively explore child and nested dataclasses
        elif is_dataclass(value):
            _process_dataclass_after(value, node, object_name)
        elif isinstance(value, (list, tuple)) and len(value) and is_dataclass(value[0]):
            for obj in value:
                _process_dataclass_after(obj, node, object_name)
        elif isinstance(value, dict):
            for key, val in value.items():
                if is_dataclass(val):
                    _process_dataclass_after(val, node, object_name)
                elif isinstance(val, (list, tuple)) and len(val) and is_dataclass(val[0]):
                    for obj in val:
                        _process_dataclass_after(obj, node, object_name)


def process_tree_after_gltf(node: Union["Asset", List]):
    """
    Set up the attributes of each component of the asset which refers to assets.
    Sometime components referred to assets by names (when loading from a glTF file).
    We convert them to references to the asset.

    Args:
        node (`Asset` or `list`):
            The node to process.
    """
    if node.__class__ in GLTF_NODES_EXTENSION_CLASS:
        _process_dataclass_after(node, node, None)

    for component_name, component in node.named_components:
        if component.__class__ in GLTF_COMPONENTS_EXTENSION_CLASS:
            _process_dataclass_after(component, node, component_name)

    # Recursively through the tree
    for child in node.tree_children:
        process_tree_after_gltf(child)


def _process_dataclass_before(obj_dataclass, node: "Asset", object_name: Optional[str] = None):
    """
    Process the dataclass before the serialization.

    Args:
        obj_dataclass ():
            The dataclass to process.
        node (`Asset`):
            The node to which the dataclass belongs.
        object_name (`str`, *optional*, defaults to `None`):
            The name of the object.
    """
    for f in fields(obj_dataclass):
        value = getattr(obj_dataclass, f.name)
        type_ = f.type
        # If the attribute of the component has the right type:
        # "Any" or "Optional[Any]" with a name attribute in the pointed object
        # Then we assume it's a node in the tree + we replace a pointer with a name of the node
        # We check the named node exist for safety
        # Note that this only investigate the fields of the dataclass
        # and thus not the "children" or "parent" attribute of an Asset, thus keeping the tree in good shape
        if type_ == Any or type_ == Optional[Any]:
            if isinstance(value, str):
                node_pointer = node.get_node(value)
                if node_pointer is None:
                    raise ValueError(
                        f"The field {f.name} '{'of component' + object_name if object_name is not None else ''}' "
                        f"of node '{node.name}' has type 'Any' "
                        f"point to a second asset called '{value}' but this second asset cannot be found "
                        f"in the asset tree. Please check the name of the second asset is correct "
                        f"and the second asset is present in the scene "
                        f"or change the type of the component to be a string."
                    )
            # And is the value of the attribute is currently a node
            if not isinstance(value, str) and hasattr(value, "name"):
                setattr(obj_dataclass, f.name, value.name)  # We convert it in the node name
        # Recursively explore child and nested dataclasses
        elif is_dataclass(value):
            _process_dataclass_before(value, node, object_name)
        elif isinstance(value, (list, tuple)) and len(value) and is_dataclass(value[0]):
            for obj in value:
                _process_dataclass_before(obj, node, object_name)
        elif isinstance(value, dict):
            for key, val in value.items():
                if is_dataclass(val):
                    _process_dataclass_before(val, node, object_name)
                elif isinstance(val, (list, tuple)) and len(val) and is_dataclass(val[0]):
                    for obj in val:
                        _process_dataclass_before(obj, node, object_name)


def process_tree_before_gltf(node: "Asset"):
    """
    Set up the attributes of each GLTFExtension tree/components of the asset which refers to assets.
    Sometime components referred to assets by names (when loading from a glTF file)
    We convert them to string of the names of the assets (which are unique)

    Args:
        node (`Asset`):
            The node to process.
    """

    if node.__class__ in GLTF_NODES_EXTENSION_CLASS:
        _process_dataclass_before(node, node, None)

    for component_name, component in node.named_components:
        if component.__class__ in GLTF_COMPONENTS_EXTENSION_CLASS:
            _process_dataclass_before(component, node, component_name)

    # Recursively through the tree
    for child in node.tree_children:
        process_tree_before_gltf(child)
