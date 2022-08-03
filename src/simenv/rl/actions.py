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
from enum import Enum
from typing import List, Optional, Union

import numpy as np

from ..assets.gltf_extension import GltfExtensionMixin


try:
    from gym import spaces
except ImportError:

    class spaces:
        class Box:
            pass

        class Discrete:
            pass  # Dummy class if gym is not installed


ALLOWED_PHYSICAL_ACTION_TYPES = [
    "add_force",
    "add_relative_force",
    "add_torque",
    "add_relative_torque",
    "add_force_at_position",
    "move_position",
    "move_relative_position",
    "move_rotation",
    "move_relative_rotation",
]


@dataclass
class ActionMapping:
    """Map a RL agent action to a physical simulator action

    Args:
        physical_action (str): the physical action to be mapped to. A string selected in:
            - "add_force": add a force to the object
            - "add_relative_force": add a force to the object in the object's local coordinate system
            - "add_torque": add a torque to the object
            - "add_relative_torque": add a torque to the object in the object's local coordinate system
            - "add_force_at_position": add a force to the object at a position in the object's local coordinate system
            - "move_position": move the object along an axis
            - "move_rotation": rotate the object around an axis
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

    physical_action: str
    axis: List[float]
    amplitude: float = 1.0
    offset: float = 0.0
    position: Optional[List[float]] = None
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None

    def __post_init__(self):
        if self.physical_action not in ALLOWED_PHYSICAL_ACTION_TYPES:
            raise ValueError(f"{self.physical_action} is not a valid physical action type")


@dataclass
class DiscreteAction(spaces.Discrete):
    r"""A gym Discrete Space where each action is mapped to a physics engine action."""
    n: int
    action_map: List[ActionMapping]
    seed: Optional[int] = None

    def __post_init__(self):
        super().__init__(n=self.n, seed=self.seed)

        if isinstance(self.action_map, ActionMapping):
            self.action_map = [self.action_map]

        if len(self.action_map) != self.n:
            raise ValueError(f"Number of action_map ({len(self.action_map)}) does not match n ({self.n})")

        if not all(isinstance(a, ActionMapping) for a in self.action_map):
            raise ValueError("All the action mapping must be ActionMapping classes")


@dataclass
class BoxAction(spaces.Box):
    """A gym Box Space with a physics magnitude linearly mapped to a physics engine magnitude."""

    low: Union[float, List[float]]
    high: Union[float, List[float]]
    action_map: List[ActionMapping]
    shape: Optional[List[int]] = None
    dtype = str
    seed: Optional[int] = None

    def __post_init__(self):
        # Gym
        if isinstance(self.low, float):
            self.low = np.array([self.low])
        if isinstance(self.high, float):
            self.high = np.array([self.high])
        if self.shape is None:
            self.shape = [1] * len(self.low)
        super().__init__(low=self.low, high=self.high, shape=self.shape, dtype=np.dtype(self.dtype), seed=self.seed)

        if not isinstance(self.action_map, (list, tuple)):
            self.action_map = [self.action_map]

        if np.isscalar(self.low) and len(self.action_map) != 1:
            raise ValueError(
                f"Number of action_map ({len(self.action_map)}) does not match shape of low ({self.low.shape})"
            )
        if not np.isscalar(self.low) and len(self.action_map) != len(self.low):
            raise ValueError(
                f"Number of action_map ({len(self.action_map)}) does not match shape of low ({self.low.shape})"
            )

        if not all(isinstance(a, ActionMapping) for a in self.action_map):
            raise ValueError("All the action mapping must be ActionMapping classes")
