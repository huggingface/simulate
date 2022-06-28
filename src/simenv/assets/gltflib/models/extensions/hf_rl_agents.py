from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HFRlAgentsActionSpace:
    """
    A serialization of a gym space
    """

    type: Optional[str] = None
    n: Optional[int] = None
    low: Optional[List[float]] = None
    high: Optional[List[float]] = None
    shape: Optional[List[int]] = None
    dtype: Optional[str] = None


@dataclass_json
@dataclass
class HFRlAgentsActionMapping:
    """
    A serialization of a mapping between gym space actions and physics
    """

    physics: str
    clip_low: Optional[float] = None
    clip_high: Optional[float] = None
    scaling: Optional[float] = 1.0
    offset: Optional[float] = 0.0
    value: Optional[float] = 1.0


@dataclass_json
@dataclass
class HFRlAgentsRewardFunction:
    """
    A serialization of a reward function
    """

    entity_a: str
    entity_b: str
    type: Optional[str] = None
    distance_metric: Optional[str] = None
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False


@dataclass_json
@dataclass
class HFRlAgentsRlComponent:
    """
    A serialization of a RL component
    """

    action_space: Optional[List[HFRlAgentsActionSpace]] = (None,)
    action_mappings: Optional[List[HFRlAgentsActionMapping]] = (None,)
    observation_devices: Optional[List[str]] = (None,)
    reward_functions: Optional[List[HFRlAgentsRewardFunction]] = (None,)
