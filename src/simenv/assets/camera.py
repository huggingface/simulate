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
""" A simenv Camera."""
import itertools
from math import radians
from typing import List, Optional, Union

from .asset import Asset


class Camera(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        width=256,
        height=256,
        aspect_ratio: Optional[float] = None,
        yfov: Optional[float] = radians(60),
        znear: Optional[float] = 0.3,
        zfar: Optional[float] = None,
        camera_type: Optional[str] = "perspective",
        xmag: Optional[float] = None,
        ymag: Optional[float] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scaling=scaling, parent=parent, children=children
        )
        self.width = width
        self.height = height

        self.aspect_ratio = aspect_ratio
        self.yfov = yfov
        self.zfar = zfar
        self.znear = znear
        self.camera_type = camera_type
        self.xmag = xmag
        self.ymag = ymag
