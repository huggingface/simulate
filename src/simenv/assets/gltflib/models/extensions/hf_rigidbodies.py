from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HFRigidbodiesRigidbody:
    """
    A Rigidbody physics primitive:


    Properties:
    """

    mass: float
    drag: Optional[float] = None
    angular_drag: Optional[float] = None
    constraints: Optional[List[str]] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class HFRigidbodies:
    """
    A collider within a scene. This extension defines colliders.

    Properties:
    colliders (list) Array of colliders
    """

    rigidbodies: Optional[List[HFRigidbodiesRigidbody]] = None
    rigidbody: Optional[int] = None
