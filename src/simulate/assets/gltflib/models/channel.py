from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel
from .target import Target


@dataclass_json
@dataclass
class Channel(BaseModel):
    """
    Targets an animation's sampler at a node's property.

    Properties:
    sampler (integer) The index of a sampler in this animation used to compute the value for the target. (Required)
    target (object) The index of the node and TRS property to target. (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    sampler: Optional[int] = None
    target: Optional[Target] = None
