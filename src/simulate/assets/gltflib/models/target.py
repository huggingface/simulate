from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class Target(BaseModel):
    """
    The index of the node and TRS property that an animation channel targets.

    Properties:
    node (integer) The index of the node to target. (Optional)
    path (string) The name of the node's TRS property to modify, or the "weights" of the Morph Targets it instantiates.
        For the "translation" property, the values that are provided by the sampler are the translation along the x, y,
        and z axes. For the "rotation" property, the values are a quaternion in the order (x, y, z, w), where w is the
        scalar. For the "scale" property, the values are the scaling factors along the x, y, and z axes. (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    node: Optional[int] = None
    path: Optional[str] = None
