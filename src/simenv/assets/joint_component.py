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
from typing import ClassVar, List, Optional, TYPE_CHECKING

from .utils import camelcase_to_snakecase

if TYPE_CHECKING:
    from .asset import Asset


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

    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    connected_asset: Optional["Asset"] = None
    drag: Optional[float] = None
    angular_drag: Optional[float] = None
    constraints: Optional[List[str]] = None
    use_gravity: Optional[bool] = None
    continuous: Optional[bool] = None
    kinematic: Optional[bool] = None

    name: Optional[str] = None

    def __post_init__(self):
        # Setup all our default values
        if self.mass is None:
            self.mass = 1.0
        self.mass = float(self.mass)
        if self.drag is None:
            self.drag = 0.0
        self.drag = float(self.drag)
        if self.angular_drag is None:
            self.angular_drag = 0.0
        self.angular_drag = float(self.angular_drag)

        if self.constraints is None:
            self.constraints = []
        for contraint in self.constraints:
            if contraint not in ALLOWED_CONSTRAINTS:
                raise ValueError(f"Contraint {contraint} not in allowed list: {ALLOWED_CONSTRAINTS}")

        if self.use_gravity is None:
            self.use_gravity = True
        if self.continuous is None:
            self.continuous = False
        if self.kinematic is None:
            self.kinematic = False

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
