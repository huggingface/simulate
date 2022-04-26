from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class Asset(BaseModel):
    """
    Metadata about the glTF asset.

    Properties:
    copyright (string): A copyright message suitable for display to credit the content creator. (Optional)
    generator (string): Tool that generated this glTF model. Useful for debugging. (Optional)
    version (string): The glTF version that this asset targets. (Required)
    minVersion (string): The minimum glTF version that this asset targets. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    copyright: Optional[str] = None
    generator: Optional[str] = None
    version: str = "2.0"
    minVersion: Optional[str] = None
