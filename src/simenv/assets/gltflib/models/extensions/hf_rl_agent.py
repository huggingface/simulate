from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HFRlAgent:
    """
    A GTLF RL Agent
    """

    color: Optional[List[float]] = None
    height: Optional[float] = None
    move_speed: Optional[float] = None
    turn_speed: Optional[float] = None
    action_name: Optional[str] = None
    action_dist: Optional[str] = None
    camera_width: Optional[int] = None
    camera_height: Optional[int] = None
    available_actions: Optional[List[str]] = None
    reward_functions: Optional[List[str]] = None
    reward_entity1s: Optional[List[str]] = None
    reward_entity2s: Optional[List[str]] = None
    reward_distance_metrics: Optional[List[str]] = None
    reward_scalars: Optional[List[float]] = None
    reward_thresholds: Optional[List[float]] = None
    reward_is_terminals: Optional[List[bool]] = None
    reward_is_collectables: Optional[List[bool]] = None
