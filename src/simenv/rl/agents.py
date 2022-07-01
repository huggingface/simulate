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

import numpy as np

from simenv.rl.actions import MappedBox, MappedDiscrete

from ..assets import Asset, Camera, Capsule, Collider
from .actions import Physics
from .components import RlComponent
from .rewards import RewardFunction


class SimpleRlAgent(Asset):
    """Create a Simple RL Agent in the Scene

        A capsule mesh with a Camera as observation device, 3 discrete actions, and a reward function as the distance to a target.

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
        reward_target: Optional[Asset] = None,
        camera_width: Optional[int] = 64,
        camera_height: Optional[int] = 64,
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
            transformation_matrix=transformation_matrix,
        )

        # Add a capsule and a camera as children
        capsule = Capsule()
        camera = Camera(width=camera_width, height=camera_height)
        self.tree_children = [capsule, camera]

        # Create a reward function if a target is provided
        rewards = None
        if reward_target is not None:
            rewards = RewardFunction(self, reward_target)

        # Create our action space mapped to physics engine
        actions = MappedDiscrete(
            n=3,
            physics=[Physics.ROTATION_Y, Physics.ROTATION_Y, Physics.POSITION_X],
            amplitudes=[-90, 90, 1.0],
        )

        self.rl_component = RlComponent(actions=actions, observations=camera, rewards=rewards)
