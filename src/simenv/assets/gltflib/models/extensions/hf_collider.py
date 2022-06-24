from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HFCollidersCollider:
    """
    A collider selected in a list of predefined shape primitives:
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    MESH = "MESH"


    Properties:
    type: Optional[str] = None
    boundingBox: List[float] = None
    mesh: Optional[int] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
    """

    type: Optional[str] = None
    boundingBox: List[float] = None
    mesh: Optional[int] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class HFColliders:
    """
    A collider within a scene. This extension defines colliders.

    Properties:
    colliders (list) Array of colliders
    """

    colliders: Optional[List[HFCollidersCollider]] = None
    collider: Optional[int] = None
