from dataclasses import dataclass, make_dataclass
from typing import Any, List, Optional

from dataclasses_json import dataclass_json

from ...gltf_extension import GLTF_EXTENSIONS_REGISTER
from .extensions.khr_lights_ponctual import KHRLightsPunctual


@dataclass_json
@dataclass
class OldExtensions:
    """
    Base model for all extensions
    """

    KHR_lights_punctual: Optional[KHRLightsPunctual] = None
    HF_custom: Optional[List[str]] = None


Extensions = dataclass_json(make_dataclass("Extensions", fields=GLTF_EXTENSIONS_REGISTER, bases=(OldExtensions,)))


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
