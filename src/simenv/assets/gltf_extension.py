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
from dataclasses import field, make_dataclass
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json


GLTF_EXTENSIONS_REGISTER = []


class GltfExtensionMixin(DataClassJsonMixin):
    """A Mixin class to create a glTF extension from a python dataclass.

    Attributes:
        extension_name: The name of the glTF extension.
        component_singular: The name of the component in the glTF extension.
        component_plural: The name of the components in the glTF extension.

    Example:
        class MyGltfExtension(GltfExtensionMixin,
                              extension_name="my_extension"):
    """

    def __init_subclass__(cls, extension_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._extension_name = extension_name

        cls._gltf_extension_cls = dataclass_json(
            make_dataclass(
                extension_name,
                [
                    ("components", Optional[List[cls]], field(default=None)),
                    ("component_id", Optional[int], field(default=None)),
                    ("component_name", Optional[str], field(default=None)),
                ],
            )
        )

        # register the component to the glTF model extensions
        for (ext_name, _, _) in GLTF_EXTENSIONS_REGISTER:
            if ext_name == extension_name:
                raise ValueError(f"The glTF extension {extension_name} is already registered.")
        GLTF_EXTENSIONS_REGISTER.append((extension_name, Optional[cls._gltf_extension_cls], field(default=None)))

        # old_extension_cls = gl.Extensions
        # gl.Extensions = dataclass_json(make_dataclass(gl.Extensions.__class__.__name__,
        #     fields=[(extension_name, Optional[List[cls._gltf_extension_cls]], field(default=None))],
        #     bases=(old_extension_cls,)))

        # gl.models.Extensions = gl.Extensions
        # gl.models.base_model.Extensions = gl.Extensions

    def _add_component_to_gltf_model(self, gltf_model_extensions) -> int:
        """Add a component to a glTF model.

        Args:
            gltf_model_extensions: The glTF model extensions.

        Returns:
            The index of the component in the glTF model extensions.
        """
        if getattr(gltf_model_extensions, self._extension_name, None) is None:
            components = [self]
            # Create a component class to store our component
            new_extension_component_cls = self._gltf_extension_cls(components=components)
            if not hasattr(gltf_model_extensions, self._extension_name):
                raise ValueError(f"The glTF model extensions does not have the {self._extension_name} extension.")
            setattr(gltf_model_extensions, self._extension_name, new_extension_component_cls)
        else:
            components = getattr(getattr(gltf_model_extensions, self._extension_name), "components")
            components.append(self)
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
        node_extension_cls = self._gltf_extension_cls(component_id=component_id, component_name=component_name)
        if not hasattr(gltf_node_extensions, self._extension_name):
            raise ValueError(f"The glTF node extensions does not have the {self._extension_name} extension.")
        setattr(gltf_node_extensions, self._extension_name, node_extension_cls)
        return self._extension_name
