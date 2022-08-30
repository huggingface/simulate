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

from .action_mapping import ActionMapping
from .gltf_extension import GltfExtensionMixin


try:
    from gym import spaces
except ImportError:

    class spaces:
        class Box:
            pass

        class Discrete:
            pass  # Dummy class if gym is not installed

        class Tuple:
            pass

        class Dict:
            pass


@dataclass
class Controller(GltfExtensionMixin, gltf_extension_name="HF_controllers", object_type="component"):
    r"""An Asset Controller can be used to move or apply force/torque to an asset.

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
class ControllerTuple(GltfExtensionMixin, gltf_extension_name="HF_controllers_tuples", object_type="component"):
    r"""Store a tuple of controllers/ActionSpaces. Associated to a gym Tuple action space

    Attributes:
        - controllers: Tuple/list of the actions
        - mapping: Tuple/list of the mappings of the actions
        - space: Tuple/list of thespacegs of the actions
    """
    controllers: List[Controller]
    seed: Optional[Union[int, List[int], np.random.Generator]] = None

    def __post_init__(self):
        self.mapping = (controller.mapping for controller in self.controllers)
        self.space = spaces.Tuple((controller.space for controller in self.controllers), seed=self.seed)


@dataclass
class ControllerDict(GltfExtensionMixin, gltf_extension_name="HF_controllers_dicts", object_type="component"):
    r"""Store a dictionary of controllers/ActionSpaces. Associated to a gym Dict action space

    Attributes:
        - controllers: Dict of the actions
        - mapping: Dict of the mappings of the actions
        - space: Dict of thespacegs of the actions
    """
    controllers: Dict[str, Controller]
    seed: Optional[Union[dict, int, np.random.Generator]] = None

    def __post_init__(self):
        self.mapping = {key: controller.mapping for key, controller in self.controllers.items()}
        self.space = spaces.Dict(
            {key: controller.space for key, controller in self.controllers.items()}, seed=self.seed
        )
