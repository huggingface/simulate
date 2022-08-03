from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass
class HFRlAgentsActions:
    """
    A serialization of a gym space with possibly a mapping between actions and physics.
    Support both gym.spaces.Box and gym.spaces.Discrete at the moment.

    Attributes:
        type: The type of the action space
        n: The number of actions if the action space is discrete, e.g gym.spaces.Discrete(n)
        low: The low bound of the action space if the action space is continuous, e.g. gym.spaces.Box()
        high: The high bound of the action space if the action space is continuous, e.g. gym.spaces.Box()
        shape: The shape of the action space if the action space is continuous, e.g. gym.spaces.Box()
        dtype: The dtype of the action space if the action space is continuous, e.g. gym.spaces.Box()

        physics: A list of mapping of the actions to a physics engine actions (one for each action if the action space is discrete)
        amplitudes: A list of amplitudes for the mapping of discrete actions to a physics engine actions (one for each action if the action space is discrete)
        scaling: A scaling factor for the mapping of the actions to a physics engine actions if the action space is continuous
        offset: An offset factor for the mapping of the actions to a physics engine actions if the action space is continuous
        clip_low: A lower bound for the mapping of the actions to a physics engine actions if the action space is continuous
        clip_high: An upper bound for the mapping of the actions to a physics engine actions if the action space is continuous
    """

    type: str
    n: Optional[int] = None
    low: Optional[List[float]] = None
    high: Optional[List[float]] = None
    shape: Optional[List[int]] = None
    dtype: Optional[str] = None

    physics: Optional[List[str]] = None
    amplitudes: Optional[List[float]] = None
    scaling: Optional[List[float]] = None
    offset: Optional[List[float]] = None
    clip_low: Optional[List[float]] = None
    clip_high: Optional[List[float]] = None


@dataclass_json
@dataclass
class HFRlAgentsReward:
    """
    A serialization of a reward function based on distances between entities.

    Attributes:
        entity_a: Name of the first entity between which the reward is computed
        entity_b: Name of the second entity between which the reward is computed
        type: The type of the reward function selected between 'dense' and 'sparse'
        distance_metric: The distance metric selected: currently only 'euclidean'
        scaling: A scaling factor for the reward
        threshold: A threshold for the reward
        is_terminal: A boolean indicating whether the reward is associated to the end of an episode
        trigger_once: A boolean indicating whether the reward is triggered only one time per episode
        reward_function_a: Reward function A when dealing with predicates such as and / or
        reward_function_b: Reward function B when dealing with predicates such as and / or
    """

    entity_a: str
    entity_b: str
    type: Optional[str] = None
    distance_metric: Optional[str] = None
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False
    is_collectable: Optional[bool] = False
    trigger_once: Optional[bool] = True
    reward_function_a: Optional["HFRlAgentsReward"] = None
    reward_function_b: Optional["HFRlAgentsReward"] = None


@dataclass_json
@dataclass
class HFRlAgentsComponent:
    """
    A serialization of a RL component
    """

    actions: Optional[HFRlAgentsActions] = None
    sensor_nodes: Optional[List[str]] = None
    rewards: Optional[List[HFRlAgentsReward]] = None


@dataclass_json
@dataclass
class HFRlAgents:
    """
    An extension defining a RL agent
    """

    agents: Optional[List[HFRlAgentsComponent]] = None
    agent: Optional[int] = None
