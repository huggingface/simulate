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
""" Some pre-built simple agents."""
import itertools
from typing import List, Optional, Union

from ..assets import Asset, Camera, Capsule, Collider
from .reward_function import RewardFunction
from .rl_component import RLComponentGrid


class SimpleRlAgent(Asset):
    """Create a Simple RL Agent in the Scene
        An Rl Agent is just an Asset with an RLComponent.

        Here we create a mesh with a Capsule and an observation device: a Camera

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    """

    dimensionality = 3  # 2 for bi-dimensional assets and 3 for tri-dimensional assets (default is 3)
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        camera_width: Optional[int] = 64,
        camera_height: Optional[int] = 64,
        reward_target: Optional[Asset] = None,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        collider: Optional[Collider] = None,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            collider=collider,
        )
        obj = Capsule()
        camera = Camera(width=camera_width, height=camera_height)
        self.tree_children = [obj, camera]

        if reward_target is not None:
            reward_function = RewardFunction(self, reward_target)
        else:
            reward_function = None

        self.rl_component = RLComponentGrid(observation_devices=camera, reward_functions=reward_function)
