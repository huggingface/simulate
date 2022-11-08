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
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import numpy as np

from ..utils import logging
from .action_mapping import ActionMapping
from .gltf_extension import GltfExtensionMixin


logger = logging.get_logger(__name__)

try:
    from gym import spaces
except ImportError:
    # Our implementation of gym space classes if gym is not installed
    logger.warning(
        "The gym library is not installed, falling back our implementation of gym.spaces. "
        "To remove this message pip install simulate[rl]"
    )
    from . import spaces


@dataclass
class Actuator(GltfExtensionMixin, gltf_extension_name="HF_actuators", object_type="component"):
    """
    An Asset Actuator can be used to move an asset in the scene.
    The actuator is designed to be a part of an Actor that manipulates a scene.

    We define:
    - the space were the actions operate (discrete, continuous), it's similar to gym spaces in RL,
        self.action_space is a gym.space (define the space action happens in and allow to sample)
    - a mapping to the physics engine behavior
        self.mapping is a list of `ActionMapping` (to physics engine behaviors)

    Args:
        mapping (`List[ActionMapping]`):
            A list of ActionMapping (to physics engine behaviors)
        actuator_tag (`str`, *optional*, defaults to "actuator")::
            A string tag for the actuator that is used to group actuators together when sending actions
            (we always have a scene-level gym dict space).
        n (`int` or `List[int]`, *optional*, defaults to `None`):
            For discrete actions, the number of possible actions.
            For multi-binary actions, the number of possible binary actions or a list of the number of possible actions
            for each dimension.
        low (`float` or `List[float]` or `np.ndarray`, *optional*, defaults to `None`):
            Low bound of continuous action space dimensions, either a float or list of floats.
        high (`float` or `List[float]` or `np.ndarray`, *optional*, defaults to `None`):
            High bound of continuous action space dimensions, either a float or list of floats.
        shape (`List[int]`, *optional*, defaults to `None`):
            Shape of continuous action space, should match low/high.
        dtype (`str`, *optional*, defaults to `"float32"`):
            Sampling type for continuous action spaces only.
    """

    mapping: List[ActionMapping]
    actuator_tag: Optional[str] = None

    # Set for a Discrete or Multi-binary space
    n: Optional[Union[int, List[int]]] = None
    # multi_binary: Optional[bool] = False  # TODO: implement multi_binary

    # Set for Multidiscrete space
    # nvec: Optional[List[int]] = None  # TODO: implement multidiscrete

    # Set for a Box space
    low: Optional[Union[float, List[float], np.ndarray]] = None
    high: Optional[Union[float, List[float], np.ndarray]] = None
    shape: Optional[List[int]] = None
    dtype: str = "float32"

    seed: Optional[int] = None

    def __post_init__(self):
        if self.actuator_tag is None:
            self.actuator_tag = "actuator"
        if not isinstance(self.actuator_tag, str):
            raise ValueError("tag should be a string")

        if isinstance(self.mapping, ActionMapping):
            self.mapping = [self.mapping]
        if not all(isinstance(a, ActionMapping) for a in self.mapping):
            raise ValueError("All the action mapping must be ActionMapping classes")

        if all((self.n is None, self.low is None, self.high is None, self.shape is None)):
            raise ValueError("At least one of n, high, low, shape should be defined")

        # create discrete/multi-binary action space
        if self.n is not None:
            if not all(attr is None for attr in [self.low, self.high, self.shape]):
                raise ValueError("For MultiDiscrete actions (n is defined), high, low, shape should be set to None.")

            if not isinstance(self.n, int):
                raise ValueError("n should be an int for discrete actions")

            # if self.multi_binary:
            #     self._action_space = spaces.MultiBinary(n=self.n, seed=self.seed)
            # else:
            self._action_space = spaces.Discrete(n=self.n, seed=self.seed)

            if len(self.mapping) != self.n:
                raise ValueError(
                    f"Number of mapping ({len(self.mapping)}) does not match the number of actions ({self.n})"
                )

        # create multi-discrete action space
        # elif self.nvec is not None:
        #     if not all(attr is None for attr in [self.n, self.low, self.high, self.shape]):
        #         raise ValueError("For discrete actions (n is defined), high, low, shape should be set to None.")

        #     self._action_space = spaces.MultiDiscrete(nvec=self.nvec, seed=self.seed)

        #     if len(self.mapping) != sum(self.nvec):
        #         raise ValueError(f"Number of mapping ({len(self.mapping)})
        #         does not match the total number of actions ({sum(self.nvec)})")

        # else create box (continuous) action space
        else:
            if not all(attr is None for attr in [self.n]):
                raise ValueError("For continuous actions n should be set to None.")

            if self.low is None and self.high is None and self.shape is None:
                raise ValueError(
                    "Action space unspecified: you should specify `n` or `nvec` (for discrete action space) "
                    "or at least one of `high`, `low`, `shape` (for continuous action space)."
                )

            dtype = np.dtype(self.dtype)

            if isinstance(self.low, (tuple, list)):
                self.low = np.array(self.low, dtype=dtype)
            if isinstance(self.high, (tuple, list)):
                self.high = np.array(self.high, dtype=dtype)

            self._action_space = spaces.Box(
                low=self.low, high=self.high, shape=self.shape, dtype=dtype, seed=self.seed
            )

            self.low = self.action_space.low.tolist()  # gym Box spaces does some shape adjustments
            self.high = self.action_space.high.tolist()  # We reuse it here to make sure we have the same arrays
            self.shape = self.action_space.shape

            if len(self.mapping) != sum(self.shape):
                raise ValueError(
                    f"Number of mapping ({len(self.mapping)}) does not match the total number of dimensions "
                    f"({sum(self.shape)})"
                )

    @property
    def action_space(self) -> Union[spaces.Discrete, spaces.Box]:
        """
        Get the action space of the actuator.

        Returns:
            action_space (`spaces.Space` or `spaces.Box`):
                The action space of the actuator.
        """
        return self._action_space


# @dataclass
# class ActuatorTuple(GltfExtensionMixin, gltf_extension_name="HF_actuators_tuples", object_type="component"):
#     r"""Store a tuple of actuators/ActionSpaces. Associated to a gym Tuple action space

#     Attributes:
#         - actuators: Tuple/list of the actions
#         - mapping: Tuple/list of the mappings of the actions
#         - space: Tuple/list of thespacegs of the actions
#     """
#     actuators: List[Actuator]
#     seed: Optional[Union[int, List[int], np.random.Generator]] = None
#     id: Optional[str] = None

#     def __post_init__(self):
#         if any(not isinstance(act, Actuator) for act in self.actuators):
#             raise ValueError("All the actuators must be Actuator classes")
#         self.mapping = (actuator.mapping for actuator in self.actuators)
#         self._action_space = spaces.Tuple((actuator.space for actuator in self.actuators), seed=self.seed)
#         self.id = list(act.id for act in self.actuators)

#     @property
#     def action_space(self) -> spaces.Tuple:
#         return self._action_space


@dataclass
class ActuatorDict(GltfExtensionMixin, gltf_extension_name="HF_actuators_dicts", object_type="component"):
    """
    Store a dictionary of actuators/ActionSpaces. Associated to a gym Dict action space

    Args:
        actuators (`Dict[str, Actuator]`):
            Dict of the actions
        seed (`int` or `Dict` or `np.random.Generator`):
            Seed for the action space
    """

    actuators: Dict[str, Actuator]
    seed: Optional[Union[dict, int, np.random.Generator]] = None

    def __post_init__(self):
        if any(not isinstance(act, Actuator) for act in self.actuators.values()):
            raise ValueError("All the actuators must be Actuator classes")
        self.mapping = {key: actuator.mapping for key, actuator in self.actuators.items()}
        self._action_space = spaces.Dict(
            {key: actuator.action_space for key, actuator in self.actuators.items()}, seed=self.seed
        )
        self.id = list(actuator.id for actuator in self.actuators.values())

    @property
    def action_space(self) -> spaces.Dict:
        """
        Get the action space of the actuator.

        Returns:
            action_space (`spaces.Dict`):
                The action space of the actuator.
        """
        return self._action_space
