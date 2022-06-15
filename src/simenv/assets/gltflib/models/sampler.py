from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Sampler(NamedBaseModel):
    """
    Texture sampler properties for filtering and wrapping modes.

    Related WebGL functions: texParameterf()

    Properties:
    magFilter (integer) Magnification filter. (Optional)
    minFilter (integer) Minification filter. (Optional)
    wrapS (integer) s wrapping mode. (Optional, default: 10497)
    wrapT (integer) t wrapping mode. (Optional, default: 10497)
    name (string) The user-defined name of this object. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    magFilter: Optional[int] = None
    minFilter: Optional[int] = None
    wrapS: Optional[int] = None
    wrapT: Optional[int] = None
