from dataclasses import dataclass
from typing import Any, List, Optional

from dataclasses_json import dataclass_json



@dataclass_json
@dataclass
class BaseModel:
    """
    Base model for all GLTF2 models

    Properties:
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    extensions: Optional["Extensions"] = None
    extras: Optional[Any] = None

# These imports had to be moved to to circular imports
from .extensions.hf_collider import HFColliders
from .extensions.hf_rigidbodies import HFRigidbodies
from .extensions.hf_rl_agents import HFRlAgents
from .extensions.khr_lights_ponctual import KHRLightsPunctual
from .extensions.hf_sensors import HFCameraSensors
from .extensions.hf_sensors import HFStateSensors


@dataclass_json
@dataclass
class Extensions:
    """
    Base model for all extensions
    """

    KHR_lights_punctual: Optional[KHRLightsPunctual] = None
    HF_colliders: Optional[HFColliders] = None
    HF_rl_agents: Optional[HFRlAgents] = None
    HF_rigidbodies: Optional[HFRigidbodies] = None
    HF_camera_sensors: Optional[HFCameraSensors] = None
    HF_state_sensors: Optional[HFStateSensors] = None
    HF_custom: Optional[List[str]] = None

