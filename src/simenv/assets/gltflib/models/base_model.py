from dataclasses import dataclass
from typing import Any, List, Optional

from dataclasses_json import dataclass_json

from .extensions.hf_collider import HF_Collider
from .extensions.khr_lights_ponctual import KHRLightsPunctual


@dataclass_json
@dataclass
class Extensions:
    """
    Base model for all extensions
    """

    KHR_lights_punctual: Optional[KHRLightsPunctual] = None
    HF_collider: Optional[HF_Collider] = None
    HF_custom: Optional[List[str]] = None


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
