import string
from ctypes import LittleEndianStructure
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class GLTF_RL_Agent:
    """
    A GTLF RL Agent
    """

    color: Optional[List[float]] = None
    height: Optional[float] = None
    move_speed: Optional[float] = None
    turn_speed: Optional[float] = None
    action_name: Optional[str] = None
    action_dist: Optional[str] = None
    available_actions: Optional[List[str]] = None


@dataclass_json
@dataclass
class GLTF_RL_Agents:
    """
    A collection of GLTFAgents
    """

    agents: Optional[List[GLTF_RL_Agent]] = None
    agent: Optional[int] = None
