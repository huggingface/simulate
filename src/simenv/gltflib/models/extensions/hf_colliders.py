from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from simenv.gltflib.enums.collider_type import ColliderType


@dataclass_json
@dataclass
class ColliderShape:
    """
    A collection of GLTF collider shapes
    """

    type: Optional[ColliderType] = None
    boundingBox: List[float] = None
    mesh: Optional[int] = None
    offsetTranslation: Optional[List[float]] = None
    intangible: Optional[bool] = None


@dataclass_json
@dataclass
class HF_Colliders:
    """
    A GLTF collider shape
    """

    shapes: Optional[List[ColliderShape]] = None
