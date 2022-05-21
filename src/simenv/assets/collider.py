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
""" A simenv Material."""
from dataclasses import dataclass
from typing import List, Optional

from ..gltflib.enums.collider_type import ColliderType


@dataclass
class Collider:
    """
    A physics collider.

    Properties:
    type (ColliderType) The shape of the collider. (Optional, default Box)
    bounding_box (number[3]) The XYZ size of the bounding box that encapsulates the collider. The collider will attempt to fill the bounding box. (Required)
    mesh (number) Index of the mesh data when using the mesh collider type. (Optional)
    offset (number[3]) The position offset of the collider relative to the object it's attached to. (Optional, default [0, 0, 0])
    intangible (boolean) Whether the collider should act as an intangible trigger. (Optiona, default False)
    """

    type: Optional[ColliderType] = None
    bounding_box: List[float] = None
    mesh: Optional[int] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
