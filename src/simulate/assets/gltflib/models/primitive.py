# Copyright 2022 The HuggingFace Authors.
# Copyright (c) 2019 Sergey Krilov
# Copyright (c) 2018 Luke Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Lint as: python3
from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json

from .attributes import Attributes
from .base_model import BaseModel


@dataclass_json
@dataclass
class Primitive(BaseModel):
    """
    Geometry to be rendered with the given material.

    Related WebGL functions: drawElements() and drawArrays()

    Properties:
    attributes (object): A dictionary object, where each key corresponds to mesh attribute semantic and each value is
        the index of the accessor containing attribute's data. (Required)
    indices (integer): The index of the accessor that contains the indices. (Optional)
    material (integer): The index of the material to apply to this primitive when rendering. (Optional)
    mode (integer): The type of primitives to render. (Optional, default: 4)
    targets (object [1-*]): An array of Morph Targets, each Morph Target is a dictionary mapping attributes (only
        POSITION, NORMAL, and TANGENT supported) to their deviations in the Morph Target. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    attributes: Attributes = field(default_factory=Attributes)
    indices: Optional[int] = None
    material: Optional[int] = None
    mode: Optional[int] = None
    targets: Optional[List[Attributes]] = None
