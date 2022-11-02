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
    "add_torque",
    "add_force_at_position",
    "change_position",
    "change_rotation",
    "do_nothing",
    "set_position",
    "set_rotation",
]


@dataclass
class ActionMapping:
    """
    Map a RL agent action to an actor physical action

    The conversion is as follows
    (where X is the RL input action and Y the physics engine action e.g. force, torque, position):
        Y = Y + (X - offset) * amplitude
    For discrete action we assume X = 1.0 so that amplitude can be used to define the discrete value to apply.

    "max_velocity_threshold" can be used to limit the max resulting velocity or angular velocity
    after the action was applied :
        - max final velocity for "add_force" actions (in m/s) –
            only apply the action if the current velocity is below this value
        - max angular velocity for "add_torque" actions (in rad/s) -
            only apply the action if the current angular velocity is below this value
        Long discussion on Unity here: https://forum.unity.com/threads/terminal-velocity.34667/

    Args:
        action (`str`):
            The physical action to be mapped to. A string selected in:
            - "add_force": apply a force to the object (at the center of mass)
                The force is given in Newton if is_impulse is False and in Newton*second if is_impulse is True.
                If is_impulse is False:
                    - the value can be considered as applied during the duration of the time step
                        (controlled by the frame rate)
                    - changing the frame rate will change the force applied at each step but will lead to the same
                        result over a given total duration.
                If is_impulse is True:
                    - the force can be considered as a velocity change applied instantaneously at the step
                    - changing the frame rate will not change the force applied at each step but will lead to the
                        different result over a given total duration.
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html)
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.AddRelativeForce.html)
            - "add_torque": add a torque to the object
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.AddTorque.html)
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.AddRelativeTorque.html)
            - "add_force_at_position": add a force to the object at a position in the object's local coordinate system
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.AddForceAtPosition.html)
            - "change_position": teleport the object along an axis
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.MovePosition.html)
            - "change_rotation": teleport the object around an axis
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.MoveRotation.html)
            - "do_nothing": step the environment with no external input.
            - "set_position": teleport the object's position to 'position'
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.MovePosition.html)
            - "set_rotation": teleport the object's rotation to 'rotation'
                (see https://docs.unity3d.com/ScriptReference/Rigidbody.MoveRotation.html)
        amplitude (`float`, *optional*, defaults to `1.0`):
            The amplitude of the action to be applied (see below for details)
        offset (`float`, *optional*, defaults to `0.0`):
            The offset of the action to be applied (see below for details)
        axis (`List[float]`):
            The axis of the action to be applied along or around.
            TODO -- shape for forces
            TODO -- shape for torques
        position (`List[float]`):
            The position of the action.
            In the case of the "add_force_at_position" action, this is the position of the force.
            In the case of the set_position, this is the position to set the object to.
        use_local_coordinates (`bool`, *optional*, defaults to `True`):
            Whether to use the local/relative coordinates of the object.
        is_impulse (`bool`, *optional*, defaults to `False`):
            Whether to apply the action as an impulse or a force.
        max_velocity_threshold (`float`, *optional*, defaults to `None`):
            When we apply a force/torque, only apply if the velocity is below this value.
    """

    action: str
    amplitude: float = 1.0
    offset: float = 0.0
    axis: Optional[List[float]] = None
    position: Optional[List[float]] = None
    use_local_coordinates: bool = True
    is_impulse: bool = False
    max_velocity_threshold: Optional[float] = None

    def __post_init__(self):
        if self.action not in ALLOWED_PHYSICAL_ACTION_TYPES:
            raise ValueError(f"{self.action} is not a valid physical action type")
