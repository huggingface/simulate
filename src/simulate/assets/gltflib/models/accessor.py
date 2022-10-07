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
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel
from .sparse import Sparse


@dataclass_json
@dataclass
class Accessor(NamedBaseModel):
    """
    A typed view into a bufferView. A bufferView contains raw binary data. An accessor provides a typed view into a
    bufferView or a subset of a bufferView similar to how WebGL's vertexAttribPointer() defines an attribute in a
    buffer.

    Properties:
    bufferView (integer): The index of the bufferView. (Optional)
    byteOffset (integer): The offset relative to the start of the bufferView in bytes. (Optional, default: 0)
    componentType (integer): The datatype of components in the attribute. (Required)
    normalized (boolean): Specifies whether integer data values should be normalized. (Optional, default: false)
    count (integer): The number of attributes referenced by this accessor. (Required)
    type (string): Specifies if the attribute is a scalar, vector, or matrix. (Required)
    max (number [1-16]): Maximum value of each component in this attribute. (Optional)
    min (number [1-16]): Minimum value of each component in this attribute. (Optional)
    sparse (object): Sparse storage of attributes that deviate from their initialization value. (Optional)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    bufferView: Optional[int] = None
    byteOffset: Optional[int] = None
    componentType: Optional[int] = None
    normalized: Optional[bool] = None
    count: Optional[int] = None
    type: Optional[str] = None
    max: Optional[List[float]] = None
    min: Optional[List[float]] = None
    sparse: Optional[Sparse] = None
