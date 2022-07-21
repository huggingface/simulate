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
from enum import Enum
from typing import List, Optional, Union

import numpy as np


try:
    from gym.spaces import Box as GymBox
    from gym.spaces import Discrete as GymDiscrete
except ImportError:

    class GymBox:
        pass  # Dummy class if gym is not installed

    class GymDiscrete:
        pass  # Dummy class if gym is not installed


class Physics(str, Enum):
    """Physics actions."""

    POSITION_X = "position_x"
    POSITION_Y = "position_y"
    POSITION_Z = "position_z"
    ROTATION_X = "rotation_x"
    ROTATION_Y = "rotation_y"
    ROTATION_Z = "rotation_z"
    VELOCITY_X = "velocity_x"
    VELOCITY_Y = "velocity_y"
    VELOCITY_Z = "velocity_z"
    ANGULAR_VELOCITY_X = "angular_velocity_x"
    ANGULAR_VELOCITY_Y = "angular_velocity_y"
    ANGULAR_VELOCITY_Z = "angular_velocity_z"


class MappedActions:
    """A generic action space mapped to physics engine actions
    We use this dummy class mostly to reference all the action with isInstance.
    """

    pass


class MappedBox(GymBox, MappedActions):
    """A gym Box Space with a physics magnitude linearly mapped to a physics engine magnitude.

    We currently force identical bound for each dimension

    MappedBox(low=-1.0, high=2.0, physics=sm.Physics.POSITION_X)
    Will map a linear input between -1 and 2 to a linear change in X position of the object.

    scaling: float, optional (default=1.0)
        scale the input to the physics engine with regard to the action
    offset: float, optional (default=0.0)
        offset the input to the physics engine with regard to the action
    clip_low: List[float], optional (default=None)
        clip the input to the physics engine with regard to the action
    clip_high: List[float], optional (default=None)
        clip the input to the physics engine with regard to the action

    Resulting conversion is as follow (where X is the RL input action and Y the physics engine action):
        Y = Y + (X - offset) * scaling
        if clip_low is not None:
            Y = max(Y, clip_low)
        if clip_high is not None:
            Y = min(Y, clip_high)
    """

    def __init__(
        self,
        low: Union[float, List[float]],
        high: Union[float, List[float]],
        shape: Optional[List[int]] = None,
        dtype=np.float32,
        seed: Optional[int] = None,
        physics: Physics = None,
        scaling: Optional[float] = 1.0,
        offset: Optional[float] = 0.0,
        clip_low: Optional[List[float]] = None,
        clip_high: Optional[List[float]] = None,
    ):
        # Gym
        if isinstance(low, float):
            low = [low]
        if isinstance(high, float):
            high = [high]
        if shape is None:
            shape = [1] * len(low)
        super().__init__(low=low, high=high, shape=shape, dtype=dtype, seed=seed)

        # Physics
        if not isinstance(physics, Physics):
            raise ValueError("physics must be a Physics enum")
        self.physics = physics
        self.scaling = scaling
        self.offset = offset

        if clip_low is not None:
            if isinstance(clip_low, float):
                clip_low = [clip_low]
            if len(clip_low) != len(low):
                raise ValueError("clip_low must have the same length as low")
        self.clip_low = clip_low

        if clip_high is not None:
            if isinstance(clip_high, float):
                clip_high = [clip_high]
            if len(clip_high) != len(high):
                raise ValueError("clip_high must have the same length as high")
        self.clip_high = clip_high


class MappedDiscrete(GymDiscrete, MappedActions):
    r"""A gym Discrete Space where each action is mapped to a physics engine action.

    MappedDiscrete(n=3,
                   physics=[sm.Physics.POSITION_X,
                            sm.Physics.ROTATION_Y,
                            sm.Physics.ROTATION_Y],
                   amplitudes=[1, 10, -10])

    Will map 3 discrete actions to 3 physics actions increments:
        Action 1 => moving in X direction with amplitude 1 meter
        Action 2 => rotating in Y direction with amplitude 10 degree
        Action 3 => rotating in Y direction with amplitude -10 degree

    Additionally, the final physics can be clipped to a certain range after conversion in amplitude.

    The resulting conversion is as follow (where X is the RL input action and Y the physics engine action):
        Y = Y + amplitude
        if clip_low is not None:
            Y = max(Y, clip_low)
        if clip_high is not None:
            Y = min(Y, clip_high)
    """

    def __init__(
        self,
        n: int,
        seed: Optional[int] = None,
        physics: List[Physics] = None,
        amplitudes: Optional[List[float]] = None,
        clip_low: Optional[List[float]] = None,
        clip_high: Optional[List[float]] = None,
    ):
        super().__init__(n=n, seed=seed)

        # Physics
        if physics is not None:
            if not isinstance(physics, list):
                raise ValueError("physics must be a list of physic actions for each discrete action")
            if not all(isinstance(p, Physics) for p in physics):
                raise ValueError("All the physics mapping must be Physics enum")
        self.physics = physics
        self.amplitudes = amplitudes

        if clip_low is not None:
            if isinstance(clip_low, float):
                clip_low = [clip_low]
            if len(clip_low) != n:
                raise ValueError("clip_low must have length equal to n")
        self.clip_low = clip_low

        if clip_high is not None:
            if isinstance(clip_high, float):
                clip_high = [clip_high]
            if len(clip_high) != n:
                raise ValueError("clip_high must have length equal to n")
        self.clip_high = clip_high
