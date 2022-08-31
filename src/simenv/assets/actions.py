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
from typing import Dict, List, Optional, Union

import numpy as np

from .gltf_extension import GltfExtensionMixin


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
    "change_position",
    "change_relative_position",
    "change_rotation",
    "change_relative_rotation",
]


@dataclass
class ActionMapping:
    """Map a RL agent action to an actor physical action

    Args:
        physical_action (str): the physical action to be mapped to. A string selected in:
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
class Action(GltfExtensionMixin, gltf_extension_name="HF_actions", object_type="component"):
    r"""Actions can be used to move or apply force/torque to an asset.

    We define:
    - the space were the action operate (discrete, continuous), it's similar to gym spaces in RL, and
    - a mapping to the physics engine behavior

    Action.space is a gym.space (define the space action happens in and allow to sample)
    Action.mapping is a list of ActionMapping (to physics engine behaviors)

    Use:
        n (int) to define n discrete action spaces (with n associated mappings)
        high/low/shape (float or list of float) to define a continuous action spaces (with a action mapping for each dimension)

    """
    mapping: List[ActionMapping]
    n: Optional[int] = None
    low: Optional[Union[float, List[float]]] = None
    high: Optional[Union[float, List[float]]] = None
    shape: Optional[List[int]] = None
    dtype: Optional[str] = None

    seed: Optional[int] = None

    def __post_init__(self):
        if not all(isinstance(a, ActionMapping) for a in self.mapping):
            raise ValueError("All the action mapping must be ActionMapping classes")
        if isinstance(self.mapping, ActionMapping):
            self.mapping = [self.mapping]

        if all((self.n is None, self.low is None, self.high is None, self.shape is None)):
            raise ValueError("At least one of n, high, low, shape should be defined")

        if self.n is not None:
            if not all((self.low is None, self.high is None, self.shape is None)):
                raise ValueError("For discrete actions (n is defined), high, low, shape should be set to None.")
            self.space = spaces.Discrete(n=self.n, seed=self.seed)

            if len(self.mapping) != self.n:
                raise ValueError(f"Number of mapping ({len(self.mapping)}) does not match n ({self.n})")
        else:
            if self.n is not None:
                raise ValueError(
                    "For continuous actions (one of high, low, shape is defined), n should be set to None."
                )

            if self.dtype is None:
                self.dtype = "float32"
            dtype = np.dtype(self.dtype)
            self.space = spaces.Box(low=self.low, high=self.high, shape=self.shape, dtype=dtype, seed=self.seed)


@dataclass
class ActionTuple(GltfExtensionMixin, gltf_extension_name="HF_action_tuples", object_type="component"):
    r"""Store a tuple of actions

    Attributes:
        - actions: Tuple/list of the actions
        - mapping: Tuple/list of the mappings of the actions
        - space: Tuple/list of thespacegs of the actions
    """
    actions: List[Action]
    seed: Optional[Union[int, List[int], np.random.Generator]] = None

    def __post_init__(self):
        self.mapping = (act.mapping for act in self.actions)
        self.space = spaces.Tuple((act.space for act in self.space), seed=self.seed)


@dataclass
class ActionDict(GltfExtensionMixin, gltf_extension_name="HF_action_dicts", object_type="component"):
    r"""Store a dictionary of actions

    Attributes:
        - actions: Dict of the actions
        - mapping: Dict of the mappings of the actions
        - space: Dict of thespacegs of the actions
    """
    actions: Dict[str, Action]
    seed: Optional[Union[dict, int, np.random.Generator]] = None

    def __post_init__(self):
        self.mapping = {key: act.mapping for key, act in self.actions.items()}
        self.space = spaces.Dict({key: act.space for key, act in self.actions.items()}, seed=self.seed)
