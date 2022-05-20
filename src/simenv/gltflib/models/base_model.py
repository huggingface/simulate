from dataclasses import dataclass
from typing import Any, Optional, Union

from dataclasses_json import dataclass_json

from .extensions.gltf_rl_agent import GLTF_RL_Agents
from .extensions.hf_colliders import HF_Colliders
from .extensions.khr_lights_ponctual import KHRLightsPunctual


@dataclass_json
@dataclass
class Extensions:
    """
    Base model for all extensions
    """

    KHR_lights_punctual: Optional[KHRLightsPunctual] = None
    GLTF_agents: Optional[GLTF_RL_Agents] = None
    HF_colliders: Optional[HF_Colliders] = None


@dataclass_json
@dataclass
class BaseModel:
    """
    Base model for all GLTF2 models

    Properties:
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    extensions: Optional[Extensions] = None
    extras: Optional[Any] = None
