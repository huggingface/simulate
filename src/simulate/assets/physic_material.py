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
""" A simulate Physic Material."""
import copy
import itertools
from dataclasses import dataclass
from typing import ClassVar, Optional

from .gltf_extension import GltfExtensionMixin
from .utils import camelcase_to_snakecase


@dataclass
class PhysicMaterial(GltfExtensionMixin, gltf_extension_name="HF_physic_materials", object_type="component"):
    """
    A physic material.

    Args:
        dynamic_friction (`float`, *optional*, defaults to `0.6`):
            The friction used when already moving. Usually a value from 0 to 1.
        static_friction (`float`, *optional*, defaults to `0.6`):
            The friction used when laying still on a surface. Usually a value from 0 to 1.
        bounciness (`float`, *optional*, defaults to `0.0`):
            How bouncy a surface is. 0 will not bounce, 1 will bounce without any loss of energy.
        friction_combine (`str`, *optional*, defaults to `"average"`):
            How the friction of two surfaces are combined.
        bounce_combine (`str`, *optional*, defaults to `"average"`):
            How the bounciness of two surfaces are combined.
    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    name: Optional[str] = None
    dynamic_friction: Optional[float] = None
    static_friction: Optional[float] = None
    bounciness: Optional[float] = None
    friction_combine: Optional[str] = None
    bounce_combine: Optional[str] = None

    def __post_init__(self):
        if self.dynamic_friction is None:
            self.dynamic_friction = 0.6
        if self.static_friction is None:
            self.static_friction = 0.6
        if self.bounciness is None:
            self.bounciness = 0.0
        if self.name is None:
            class_id = next(self.__class__.__NEW_ID)
            self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{class_id:02d}")

    def __hash__(self) -> int:
        return id(self)

    def copy(self) -> "PhysicMaterial":
        """
        Return a copy of the current object.

        Returns:
            physic_material (`PhysicMaterial`):
                The copied object.
        """
        copy_mat = copy.deepcopy(self)
        class_id = next(self.__class__.__NEW_ID)
        self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{class_id:02d}")
        return copy_mat
