from dataclasses import dataclass
from typing import Any, Optional

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

    extensions: Optional[Any] = None
    extras: Optional[Any] = None
