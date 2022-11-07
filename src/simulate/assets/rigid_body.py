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
""" A simulate RigidBodyComponent."""
import itertools
from dataclasses import dataclass
from typing import ClassVar, List, Optional

from .gltf_extension import GltfExtensionMixin


ALLOWED_CONSTRAINTS = [
    "freeze_position_x",
    "freeze_position_y",
    "freeze_position_z",
    "freeze_rotation_x",
    "freeze_rotation_y",
    "freeze_rotation_z",
]

ALLOWED_COLLISION_DETECTION = ["discrete", "continuous"]


@dataclass()
class RigidBodyComponent(GltfExtensionMixin, gltf_extension_name="HF_rigid_bodies", object_type="component"):
    """
    A rigid body characteristics that can be added to a primitive.

    Args:
        name (`string`, *optional*, defaults to `None`):
            The user-defined name of this material.
        mass (`float`, *optional*, defaults to `1.0`):
            Mass of the rigidbody.
        center_of_mass (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            Center of mass of the rigidbody.
        inertia_tensor (`List[float]`, *optional*, defaults to `None`):
            Inertia tensor of the rigidbody.
        linear_drag (`float`, *optional*, defaults to `0.0`):
            Linear drag of the rigidbody.
        angular_drag (`float`, *optional*, defaults to `0.0`):
            Angular drag of the rigidbody.
        constraints (List[str], *optional*, defaults to `[]`):
            List of constraints to apply to the rigidbody, selected in:
                [    "freeze_position_x",
                    "freeze_position_y",
                    "freeze_position_z",
                    "freeze_rotation_x",
                    "freeze_rotation_y",
                    "freeze_rotation_z",
                ]
        use_gravity (`bool`, *optional*, defaults to `True`):
            Whether the rigidbody should ignore gravity.
        collision_detection (`str`, *optional*, defaults to `"discrete"`):
            Whether to use discrete or continuous collision detection, for slower but more precise collision detection
            (recommended for small but fast-moving objects).
        kinematic (`bool`, *optional*, defaults to `False`):
            Set to True to ignore force collisions and treat the rigidbody as a fix/static object.
            Equivalent to isKinematic in Unity, custom_integrator in Godot and a mass = 0 in Bullet.

    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    name: Optional[str] = None
    mass: Optional[float] = None
    center_of_mass: Optional[List[float]] = None
    inertia_tensor: Optional[List[float]] = None
    linear_drag: Optional[float] = None
    angular_drag: Optional[float] = None
    constraints: Optional[List[str]] = None
    use_gravity: Optional[bool] = None
    collision_detection: Optional[str] = None
    kinematic: Optional[bool] = None

    def __post_init__(self):
        # Setup all our default values
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

        if self.linear_drag is None:
            self.linear_drag = 0.0
        self.linear_drag = float(self.linear_drag)

        if self.angular_drag is None:
            self.angular_drag = 0.0
        self.angular_drag = float(self.angular_drag)

        if self.constraints is None:
            self.constraints = []
        for constraint in self.constraints:
            if constraint not in ALLOWED_CONSTRAINTS:
                raise ValueError(f"Constraint {constraint} not in allowed list: {ALLOWED_CONSTRAINTS}")

        if self.use_gravity is None:
            self.use_gravity = True

        if self.collision_detection is None:
            self.collision_detection = "discrete"
        if self.collision_detection not in ALLOWED_COLLISION_DETECTION:
            raise ValueError(
                f"Collision detection {self.collision_detection} not in allowed list: {ALLOWED_COLLISION_DETECTION}"
            )

        if self.kinematic is None:
            self.kinematic = False

    def __hash__(self) -> int:
        return id(self)
