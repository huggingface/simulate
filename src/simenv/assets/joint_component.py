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
""" A simenv JointComponent."""
import copy
import itertools
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, List, Optional

from .utils import camelcase_to_snakecase


if TYPE_CHECKING:
    from .asset import Asset

ALLOWED_JOINT_TYPES = ["fixed", "slider", "hinge"]


@dataclass()
class JointComponent:
    """
    A joint can be added to connect together two assets with Rigidbodies component and constrain them to
    move like they are connected by a hinge.

    Parameters
    ----------
    name : string, optional
        The user-defined name of this material

    connected_asset : Asset, optional
        The asset to which this joint is connected.
        If not set, the joint connects to the world.

    type: string, optional
        The type of joint to use.
        - "fixed": no movement allowed
        - "slider": only translation along 1 axis allowed
        - "hinge": only rotation along 1 axis allowed

    axis: List[float], optional
        The axis along which the joint is allowed to move (translation or rotation).

    anchor: List[float], optional
        Position of the anchor point of the joint.

    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    connected_asset: "Asset"
    type: str
    axis: List[float]
    anchor: Optional[List[float]] = None
    linear_damping: Optional[float] = 0.0
    angular_damping: Optional[float] = 0.0
    joint_friction: Optional[float] = 0.0
    drive_stifness: Optional[float] = 0.0
    drive_damping: Optional[float] = 0.0
    drive_force_limit: Optional[float] = 0.0
    drive_target: Optional[float] = 0.0
    drive_target_velocity: Optional[float] = 0.0
    is_limited: Optional[bool] = False
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None

    name: Optional[str] = None

    def __post_init__(self):
        # Setup all our default values
        self.type = self.type.lower()
        if self.type not in ALLOWED_JOINT_TYPES:
            raise ValueError(f"Joint type {self.type} is not allowed. Allowed types are: {ALLOWED_JOINT_TYPES}")

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
