from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json

from .attributes import Attributes
from .base_model import BaseModel


@dataclass_json
@dataclass
class Primitive(BaseModel):
    """
    Geometry to be rendered with the given material.

    Related WebGL functions: drawElements() and drawArrays()

    Properties:
    attributes (object): A dictionary object, where each key corresponds to mesh attribute semantic and each value is
        the index of the accessor containing attribute's data. (Required)
    indices (integer): The index of the accessor that contains the indices. (Optional)
    material (integer): The index of the material to apply to this primitive when rendering. (Optional)
    mode (integer): The type of primitives to render. (Optional, default: 4)
    targets (object [1-*]): An array of Morph Targets, each Morph Target is a dictionary mapping attributes (only
        POSITION, NORMAL, and TANGENT supported) to their deviations in the Morph Target. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    attributes: Attributes = field(default_factory=Attributes)
    indices: Optional[int] = None
    material: Optional[int] = None
    mode: Optional[int] = None
    targets: Optional[List[Attributes]] = None
