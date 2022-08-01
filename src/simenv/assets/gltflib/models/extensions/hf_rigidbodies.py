from dataclasses import dataclass
from typing import Any, List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HFRigidbodies:
    """
    A rigidbody within a scene. This extension defines rigidbodies.

    Properties:
    rigidbodies (list) Array of rigidbodies
    """

    rigidbodies: Optional[List[Any]] = None
    rigidbody: Optional[int] = None
