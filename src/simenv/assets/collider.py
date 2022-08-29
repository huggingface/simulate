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
from dataclasses import dataclass
from typing import List, Optional

from .gltf_extension import GltfExtensionMixin


ALLOWED_COLLIDER_TYPES = ["box", "sphere", "capsule", "mesh"]


@dataclass
class Collider(GltfExtensionMixin, gltf_extension_name="HF_colliders", object_type="component"):
    """
    A physics collider.

    Properties:
    bounding_box (number[3]) The XYZ size of the bounding box that encapsulates the collider. The collider will attempt to fill the bounding box.
    type (str) The shape of the collider. (Optional, default "box")
    mesh (number) Index of the mesh data when using the mesh collider type. (Optional)
    offset (number[3]) The position offset of the collider relative to the object it's attached to. (Optional, default [0, 0, 0])
    intangible (boolean) Whether the collider should act as an intangible trigger. (Optiona, default False)
    convex (boolean) Whether the collider is convex when using the mesh collider type. (Optional)
    """

    bounding_box: List[float]
    type: Optional[str] = None
    mesh: Optional[int] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
    convex: Optional[bool] = None

    def __post_init__(self):
        if len(self.bounding_box) != 3:
            raise ValueError("Collider bounding_box must be a list of 3 numbers")
        if self.type is None:
            self.type = "box"
        if self.type not in ALLOWED_COLLIDER_TYPES:
            raise ValueError(f"Collider type {self.type} is not supported.")
