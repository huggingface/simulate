from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Buffer(NamedBaseModel):
    """
    A buffer points to binary geometry, animation, or skins.

    Properties:
    uri (string): The uri of the buffer. (Optional)
    byteLength (integer): The total byte length of the buffer view. (Required)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    uri: Optional[str] = None
    byteLength: Optional[int] = None
