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


@dataclass_json
@dataclass
class Node(NamedBaseModel):
    """
    A node in the node hierarchy. When the node contains skin, all mesh.primitives must contain JOINTS_0 and
    WEIGHTS_0 attributes. A node can have either a matrix or any combination of translation/rotation/scale (TRS)
    properties. TRS properties are converted to matrices and postmultiplied in the T * R * S order to compose the
    transformation matrix; first the scale is applied to the vertices, then the rotation, and then the translation.
    If none are provided, the transform is the identity. When a node is targeted for animation (referenced by an
    animation.channel.target), only TRS properties may be present; matrix will not be present.

    Properties:
    camera (integer): The index of the camera referenced by this node. (Optional)
    children (integer [1-*]): The indices of this node's children. (Optional)
    skin (integer): The index of the skin referenced by this node. (Optional)
    matrix (number [16]): A floating-point 4x4 transformation matrix stored in column-major order. (Optional, default:
        [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])
    mesh (integer): The index of the mesh in this node. (Optional)
    rotation (number [4]): The node's unit quaternion rotation in the order (x, y, z, w), where w is the scalar.
        (Optional, default: [0,0,0,1])
    scale (number [3]): The node's non-uniform scale, given as the scaling factors along the x, y, and z axes.
        (Optional, default: [1,1,1])
    translation (number [3]): The node's translation along the x, y, and z axes. (Optional), default: [0,0,0]
    weights (number [1-*]): The weights of the instantiated Morph Target. Number of elements must match number of Morph
        Targets of used mesh. (Optional)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    camera: Optional[int] = None
    children: Optional[List[int]] = None
    skin: Optional[int] = None
    matrix: Optional[List[float]] = None
    mesh: Optional[int] = None
    rotation: Optional[List[float]] = None
    scale: Optional[List[float]] = None
    translation: Optional[List[float]] = None
    weights: Optional[List[float]] = None
