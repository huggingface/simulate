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
""" A simulate JointComponent."""
import itertools
from dataclasses import dataclass
from typing import ClassVar, List, Optional

from .gltf_extension import GltfExtensionMixin


ALLOWED_JOINT_TYPES = ["fixed", "prismatic", "revolute"]


@dataclass()
class ArticulationBodyComponent(
    GltfExtensionMixin, gltf_extension_name="HF_articulation_bodies", object_type="component"
):
    """
    An articulation body will model the physics of an articulation body connecting together an asset
    with its parent in the hierarchy.

    Parameters
    ----------
    name : string, optional
        The user-defined name of this material

    joint_type: string, optional
        The type of articulation (aka joint) to use.
        - "fixed": no movement allowed
        - "slider": only translation along 1 axis allowed
        - "hinge": only rotation along 1 axis allowed

    anchor_rotation: List[float], optional
        The rotation axis along which the asset is allowed to move relative to its parent (translation or rotation).

    anchor_position: List[float], optional
        Position of the anchor point of the joint.

    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    joint_type: str
    anchor_rotation: List[float] = None
    anchor_position: Optional[List[float]] = None
    immovable: Optional[bool] = None
    linear_damping: float = 0.0
    angular_damping: float = 0.0
    joint_friction: float = 0.0
    drive_stiffness: float = 0.0
    drive_damping: float = 0.0
    drive_force_limit: float = 0.0
    drive_target: float = 0.0
    drive_target_velocity: float = 0.0
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None

    mass: Optional[float] = None
    center_of_mass: Optional[List[float]] = None
    inertia_tensor: Optional[List[float]] = None
    use_gravity: Optional[bool] = None
    collision_detections: Optional[str] = None  # TODO: see if we want to keep this one

    def __post_init__(self):
        # Setup all our default values
        self.joint_type = self.joint_type.lower()
        if self.joint_type not in ALLOWED_JOINT_TYPES:
            raise ValueError(f"Joint type {self.joint_type} is not allowed. Allowed types are: {ALLOWED_JOINT_TYPES}")

        if self.anchor_rotation is None:
            self.anchor_rotation = [0.0, 0.0, 0.0, 1.0]
        if len(self.anchor_rotation) != 4:
            raise ValueError("anchor_rotation must be a list of 4 floats (Quaternion)")

        if self.anchor_position is None:
            self.anchor_position = [0.0, 0.0, 0.0]
        if len(self.anchor_position) != 3:
            raise ValueError("anchor_position must be a list of 3 floats")

        if self.immovable is None:
            self.immovable = False

        if self.linear_damping is None:
            self.linear_damping = 0.0
        self.linear_damping = float(self.linear_damping)

        if self.angular_damping is None:
            self.angular_damping = 0.0
        self.angular_damping = float(self.angular_damping)

        if self.mass is None:
            self.mass = 1.0
        self.mass = float(self.mass)

        if self.center_of_mass is None:
            self.center_of_mass = [0.0, 0.0, 0.0]
        if len(self.center_of_mass) != 3:
            raise ValueError("center_of_mass must be a list of 3 floats")

        if self.inertia_tensor is not None:
            if len(self.inertia_tensor) != 3:
                raise ValueError("inertia_tensor must be a list of 3 floats")
