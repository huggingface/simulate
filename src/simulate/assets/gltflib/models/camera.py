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
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel
from .orthographic_camera_info import OrthographicCameraInfo
from .perspective_camera_info import PerspectiveCameraInfo


@dataclass_json
@dataclass
class Camera(NamedBaseModel):
    """
    A camera's projection. A node can reference a camera to apply a transform to place the camera in the scene.

    Properties:
    orthographic (object) An orthographic camera containing properties to create an orthographic projection matrix.
        (Optional)
    perspective (object) A perspective camera containing properties to create a perspective projection matrix.
        (Optional)
    type (string) Specifies if the camera uses a perspective or orthographic projection. (Required)
    name (string) The user-defined name of this object. (Optional)
    width (int) The width of the camera render result. (Optional)
    height (int) The height of the camera render result. (Optional)s
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    orthographic: Optional[OrthographicCameraInfo] = None
    perspective: Optional[PerspectiveCameraInfo] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
