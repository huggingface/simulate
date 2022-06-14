from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Scene(NamedBaseModel):
    """
    The root nodes of a scene.

    Properties:
    nodes (integer [1-*]) The indices of each root node. (Optional)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    nodes: Optional[List[int]] = None
