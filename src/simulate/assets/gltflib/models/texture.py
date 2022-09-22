from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Texture(NamedBaseModel):
    """
    A texture and its sampler.

    Related WebGL functions: createTexture(), deleteTexture(), bindTexture(), texImage2D(), and texParameterf()

    Properties:
    sampler (integer) The index of the sampler used by this texture. When undefined, a sampler with repeat wrapping and
        auto filtering should be used. (Optional)
    source (integer) The index of the image used by this texture. When undefined, it is expected that an extension or
        other mechanism will supply an alternate texture source, otherwise behavior is undefined. (Optional)
    name (string) The user-defined name of this object. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    sampler: Optional[int] = None
    source: Optional[int] = None
