from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from ...enums.collider_type import ColliderType


@dataclass_json
@dataclass
class HF_Collider:
    """
    A GLTF collider
    """

    type: Optional[ColliderType] = None
    boundingBox: List[float] = None
    mesh: Optional[int] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
