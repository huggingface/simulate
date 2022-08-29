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
""" Some mapping from Discrete and Box Spaces to physics actions."""
from dataclasses import dataclass
from typing import List, Optional


ALLOWED_PHYSICAL_ACTION_TYPES = [
    "add_force",
    "add_relative_force",
    "add_torque",
    "add_relative_torque",
    "add_force_at_position",
    "change_position",
    "change_relative_position",
    "change_rotation",
    "change_relative_rotation",
    "set_position",
    "set_rotation",
]


@dataclass
class ActionMapping:
    """Map a RL agent action to an actor physical action

    Args:
        action (str): the physical action to be mapped to. A string selected in:
            - "add_force": add a force to the object
            - "add_relative_force": add a force to the object in the object's local coordinate system
            - "add_torque": add a torque to the object
            - "add_relative_torque": add a torque to the object in the object's local coordinate system
            - "add_force_at_position": add a force to the object at a position in the object's local coordinate system
            - "change_position": move the object along an axis
            - "move_position_relative": move the object along an axis in local coordinates
            - "rotate": rotate the object around an axis
            - "change_relative_rotation": rotate the object along an axis in local coordinates
        axis (List[float]): the axis of the action to be applied along or around
        amplitude (float): the amplitude of the action to be applied (see below for details)
        offset (float): the offset of the action to be applied (see below for details)
        position (List[float]): the position of the action to be applied
            (in the special case of the "add_force_at_position" action, this is the position of the force)
        upper_limit (float): the upper limit of the resulting physical action (see below for details)
        lower_limit (float): the lower limit of the resulting physical action (see below for details)

    The conversion is as follow (where X is the RL input action and Y the physics engine action e.g. force, torque, position):
        Y = Y + (X - offset) * amplitude
        if clip_low is not None:
            Y = max(Y, clip_low)
        if clip_high is not None:
            Y = min(Y, clip_high)
    In the case of discrete action we assume X = 1.0 so that amplitude can be used to define the discrete value to apply.
    """

    action: str
    axis: List[float]
    amplitude: float = 1.0
    offset: float = 0.0
    position: Optional[List[float]] = None
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None

    def __post_init__(self):
        if self.action not in ALLOWED_PHYSICAL_ACTION_TYPES:
            raise ValueError(f"{self.action} is not a valid physical action type")
