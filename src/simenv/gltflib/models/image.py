from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Image(NamedBaseModel):
    """
    Image data used to create a texture. Image can be referenced by URI or bufferView index. mimeType is required in the
    latter case.

    Properties:
    uri (string) The uri of the image. (Optional)
    mimeType (string) The image's MIME type. (Optional)
    bufferView (integer) The index of the bufferView that contains the image. Use this instead of the image's uri
        property. (Optional)
    name (string) The user-defined name of this object. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    uri: Optional[str] = None
    mimeType: Optional[str] = None
    bufferView: Optional[int] = None
