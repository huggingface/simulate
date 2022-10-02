from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel
from .primitive import Primitive


@dataclass_json
@dataclass
class Mesh(NamedBaseModel):
    """
    A set of primitives to be rendered. A node can contain one mesh. A node's transform places the mesh in the scene.

    Properties:
    primitives (primitive [1-*]): An array of primitives, each defining geometry to be rendered with a material.
        (Required)
    weights (number [1-*]): Array of weights to be applied to the Morph Targets. (Optional)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    primitives: Optional[List[Primitive]] = None
    weights: Optional[List[float]] = None
