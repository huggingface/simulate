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
""" A simenv Collider."""
import itertools
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, List, Optional, Union

from .asset import Asset
from .gltf_extension import GltfExtensionMixin


ALLOWED_COLLIDER_TYPES = ["box", "sphere", "capsule", "mesh"]


@dataclass
class Collider(Asset, GltfExtensionMixin, gltf_extension_name="HF_colliders", object_type="node"):
    """
    A physics collider.

    Properties:
    type (str) The shape of the collider. (Optional, default "box")
    bounding_box (number[3]) The XYZ size of the bounding box that encapsulates the collider. The collider will attempt to fill the bounding box. (Optional)
    mesh (number) A mesh when using the mesh collider type. (Optional)
    offset (number[3]) The position offset of the collider relative to the object it's attached to. (Optional, default [0, 0, 0])
    intangible (boolean) Whether the collider should act as an intangible trigger. (Optiona, default False)
    convex (boolean) Whether the collider is convex when using the mesh collider type. (Optional)
    """

    type: Optional[str] = None
    bounding_box: List[float] = None
    mesh: Optional[Any] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
    convex: Optional[bool] = None

    name: InitVar[Optional[str]] = None
    position: InitVar[Optional[List[float]]] = None
    rotation: InitVar[Optional[List[float]]] = None
    scaling: InitVar[Optional[Union[float, List[float]]]] = None
    transformation_matrix: InitVar[Optional[List[float]]] = None
    parent: InitVar[Optional[Any]] = None
    children: InitVar[Optional[List[Any]]] = None
    created_from_file: InitVar[Optional[str]] = None

    __NEW_ID: ClassVar[Any] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __post_init__(
        self, name, position, rotation, scaling, transformation_matrix, parent, children, created_from_file
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            transformation_matrix=transformation_matrix,
            parent=parent,
            children=children,
            created_from_file=created_from_file,
        )

        if self.type is None:
            if self.mesh is not None:
                self.type = "mesh"
            else:
                self.type = "box"

        if self.type not in ALLOWED_COLLIDER_TYPES:
            raise ValueError(f"Collider type {self.type} is not supported.")

        if self.bounding_box is None and self.mesh is None:
            raise ValueError(
                "You should provide either a bounding box (for box, sphere and capsule colliders) or a mesh."
            )

        if self.bounding_box is not None and len(self.bounding_box) != 3:
            raise ValueError("Collider bounding_box must be a list of 3 numbers")
