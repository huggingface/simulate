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
""" A simenv RigidBody."""
import copy
import itertools
from dataclasses import dataclass
from typing import ClassVar, List, Optional

import numpy as np
import pyvista

from .utils import camelcase_to_snakecase


# TODO thom this is a very basic PBR Metrial class, mostly here to be able to load a gltf - strongly base on GLTF definitions
# To be revamped and improved later

"FreezePositionX"
"FreezePositionY"
"FreezePositionZ"
"FreezeRotationX"
"FreezeRotationY"
"FreezeRotationZ"
"FreezePosition"
"FreezeRotation"
"FreezeAll"


@dataclass()
class RigidBody:
    """
    A rigid body caracteristics that can be added to a primitive.

    Parameters
    ----------
    name : string, optional
        The user-defined name of this material

    mass : List, optiona

    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    mass: Optional[float] = None

    constraints: Optional[List[str]] = None

    name: Optional[str] = None

    def __post_init__(self):
        # Setup all our default values
        if self.mass is None:
            self.mass = 1.0

        if self.name is None:
            id = next(self.__class__.__NEW_ID)
            self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{id:02d}")

    def __hash__(self):
        return id(self)

    def copy(self):
        copy_rb = copy.deepcopy(self)
        id = next(self.__class__.__NEW_ID)
        self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{id:02d}")
        return copy_rb
