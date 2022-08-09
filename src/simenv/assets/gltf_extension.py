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
from typing import TYPE_CHECKING, Any, List, Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json


if TYPE_CHECKING:
    from .asset import Asset

GLTF_EXTENSIONS_REGISTER = []


class GltfExtensionMixin(DataClassJsonMixin):
    """A Mixin class to extend a python dataclass to be a glTF extension.

        Requirements:
            - The extended python class must be a dataclass.
            - The attributes of the class must be
                * either JSON serializable, or
                * an Asset object to which the type should then be Union[str, Any]
                  (converted in a string with the node name while saving to glTF and
                   decoded to a pointer to the asset object while loading from glTF).

    Attributes:
        gltf_extension_name: The name of the glTF extension.

    Example:
        class MyGltfExtension(GltfExtensionMixin,
                              gltf_extension_name="my_extension"):
    """

    def __init_subclass__(cls, gltf_extension_name, **kwargs):
        super().__init_subclass__(**kwargs)
        if not gltf_extension_name:
            raise ValueError("A glTF extension name must be provided.")
        cls._gltf_extension_name = gltf_extension_name

        cls._gltf_extension_cls = dataclass_json(
            make_dataclass(
                gltf_extension_name,
                [
                    ("components", Optional[List[cls]], field(default=None)),
                    ("component_id", Optional[int], field(default=None)),
                    ("name", Optional[str], field(default=None)),
                ],
            )
        )

        # register the component to the glTF model extensions
        for (ext_name, _, _) in GLTF_EXTENSIONS_REGISTER:
            if ext_name == gltf_extension_name:
                raise ValueError(f"The glTF extension {gltf_extension_name} is already registered.")
        GLTF_EXTENSIONS_REGISTER.append((gltf_extension_name, Optional[cls._gltf_extension_cls], field(default=None)))

    def _add_component_to_gltf_model(self, gltf_model_extensions) -> int:
        """Add a component to a glTF model.

        Args:
            gltf_model_extensions: The glTF model extensions.

        Returns:
            The index of the component in the glTF model extensions.
        """
        copy_self = copy.deepcopy(self)
        if getattr(gltf_model_extensions, self._gltf_extension_name, None) is None:
            components = [copy_self]
            # Create a component class to store our component
            new_extension_component_cls = self._gltf_extension_cls(components=components)
            if not hasattr(gltf_model_extensions, self._gltf_extension_name):
                raise ValueError(f"The glTF model extensions does not have the {self._gltf_extension_name} extension.")
            setattr(gltf_model_extensions, self._gltf_extension_name, new_extension_component_cls)
        else:
            components = getattr(getattr(gltf_model_extensions, self._gltf_extension_name), "components")
            components.append(copy_self)
        component_id = len(components) - 1
        return component_id

    def _add_component_to_gltf_node(self, gltf_node_extensions, component_id: int, component_name: str) -> str:
        """
        Add a component to a glTF node.

        Args:
            gltf_node_extensions: The glTF node extensions dataclass_json.
            component_id: The index of the component in the glTF model extensions.

        Returns:
            The name of the glTF node extensions.
        """
        node_extension_cls = self._gltf_extension_cls(component_id=component_id, name=component_name)
        if not hasattr(gltf_node_extensions, self._gltf_extension_name):
            raise ValueError(f"The glTF node extensions does not have the {self._gltf_extension_name} extension.")
        setattr(gltf_node_extensions, self._gltf_extension_name, node_extension_cls)
        return self._gltf_extension_name


def _process_dataclass_after(obj_dataclass, node):
    for f in fields(obj_dataclass):
        value = getattr(obj_dataclass, f.name)
        type_ = f.type
        # If the attribute of the component has the right type ("Union[str, Asset]")
        if type_ == Any:
            if isinstance(value, str):
                node_pointer = node.get_node(value)
                setattr(obj_dataclass, f.name, node_pointer)  # We convert it in the node pointer
        # Recursively explore child and nested dataclasses
        elif is_dataclass(value):
            _process_dataclass_after(value, node)
        elif isinstance(value, (list, tuple)) and len(value) and is_dataclass(value[0]):
            for obj in value:
                _process_dataclass_after(obj, node)
        elif isinstance(value, dict):
            for key, val in value.items():
                if is_dataclass(val):
                    _process_dataclass_after(val, node)
                elif isinstance(val, (list, tuple)) and len(val) and is_dataclass(val[0]):
                    for obj in val:
                        _process_dataclass_after(obj, node)


def process_components_after_gltf(node: "Asset"):
    """Setup the attributes of each components of the asset which refere to assets.
    Sometime components refered to assets by names (when loading from a glTF file)
    We convert them to references to the asset
    """
    for component in node.components:
        _process_dataclass_after(component, node)

    # Recursively through the tree
    for child in node.tree_children:
        process_components_after_gltf(child)


def _process_dataclass_before(obj_dataclass, node, component_name):
    for f in fields(obj_dataclass):
        value = getattr(obj_dataclass, f.name)
        type_ = f.type
        # If the attribute of the component has the right type ("Union[str, Asset]")
        if type_ == Any:
            if isinstance(value, str):
                node_pointer = node.get_node(value)
                if node_pointer is None:
                    raise ValueError(
                        f"The field {f.name} of component '{component_name}' of node '{node.name}' has type 'Any' "
                        f"point to a second asset called '{value}' but this second asset cannot be found "
                        f"in the asset tree. Please check the name of the second asset is correct "
                        "and the second asset is present in the scene or change the type of the component to be a string."
                    )
            # And is the value of the attribute is currently a node
            if not isinstance(value, str) and hasattr(value, "name"):
                setattr(obj_dataclass, f.name, value.name)  # We convert it in the node name
        # Recursively explore child and nested dataclasses
        elif is_dataclass(value):
            _process_dataclass_before(value, node, component_name)
        elif isinstance(value, (list, tuple)) and len(value) and is_dataclass(value[0]):
            for obj in value:
                _process_dataclass_before(obj, node, component_name)
        elif isinstance(value, dict):
            for key, val in value.items():
                if is_dataclass(val):
                    _process_dataclass_before(val, node, component_name)
                elif isinstance(val, (list, tuple)) and len(val) and is_dataclass(val[0]):
                    for obj in val:
                        _process_dataclass_before(obj, node, component_name)


def process_components_before_gltf(node: "Asset"):
    """Setup the attributes of each components of the asset which refere to assets.
    Sometime components refered to assets by names (when loading from a glTF file)
    We convert them to string of the names of the assets (which are unique)
    """

    for component_name, component in node.named_components:
        _process_dataclass_before(component, node, component_name)

    # Recursively through the tree
    for child in node.tree_children:
        process_components_before_gltf(child)
