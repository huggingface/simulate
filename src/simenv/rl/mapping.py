from dataclasses import dataclass
from optparse import Option
from typing import List, Optional


ALLOWED_PHYSICS = [
    "position_x",
    "position_y",
    "position_z",
    "rotation_x",
    "rotation_y",
    "rotation_z",
    "velocity_x",
    "velocity_y",
    "velocity_z",
    "angular_velocity_x",
    "angular_velocity_y",
    "angular_velocity_z",
]


@dataclass
class GenericActionMapping:
    physics: str
    clip_low: Optional[float] = None
    clip_high: Optional[float] = None

    def __post_init__(self):
        if self.physics not in ALLOWED_PHYSICS:
            raise ValueError(
                f"{self.physics} is not a valid physics magnitude to modify, should be in {ALLOWED_PHYSICS}"
            )


@dataclass
class Continuous(GenericActionMapping):
    scaling: Optional[float] = 1.0
    offset: Optional[float] = 0.0


@dataclass
class Discrete(GenericActionMapping):
    value: Optional[float] = 1.0


# TODO remove if we want to

# class DiscreteRLAgentActions(RLAgentActions):
#     def __init__(self, name=None, dist=None, available_actions=None) -> None:
#         super().__init__(name=name, dist=dist, available_actions=available_actions)

#     @classmethod
#     def default(cls):
#         return cls(
#             name="movement",
#             dist="discrete",
#             available_actions=["move_forward", "move_backward", "move_left", "move_right", "turn_left", "turn_right"],
#         )


# class ContinuousRLAgentActions(RLAgentActions):
#     def __init__(self, name=None, dist=None, types=None, available_actions=None) -> None:
#         super().__init__(name=name, dist=dist, types=types, available_actions=available_actions)

#     @classmethod
#     def default(cls):
#         return cls(
#             name="movement",
#             dist="continuous",
#             available_actions=["move_forward_backward", "move_right_left", "turn_right_left"],
#         )
