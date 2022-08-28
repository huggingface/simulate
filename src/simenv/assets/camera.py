# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" A simenv Camera."""
import itertools
from typing import List, Optional, Union

import numpy as np


try:
    from gym import spaces
except:
    pass

from .asset import Asset
from .collider import Collider


ALLOWED_CAMERA_TYPES = ["perspective", "orthographic"]


class Camera(Asset):
    """A Camera asset.
    This Camera is located at the origin by default and has no rotation.

    Args:
        width: The width of the Camera. Default: 256
        height: The height of the Camera. Default: 256
        aspect_ratio: The aspect ratio of the Camera if needed
        yfov: The vertical field of view of the Camera in degrees. Default: 60 degrees
        znear: The near clipping plane of the Camera.
        zfar: The far clipping plane of the Camera.
        camera_type: The type of camera.
        xmag: The x magnification of the Camera.
        ymag: The y magnification of the Camera.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        width=256,
        height=256,
        camera_type: Optional[str] = "perspective",
        znear: Optional[float] = 0.3,
        yfov: Optional[float] = 60,
        aspect_ratio: Optional[float] = None,
        zfar: Optional[float] = None,
        xmag: Optional[float] = None,
        ymag: Optional[float] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        collider: Optional[Collider] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            collider=collider,
        )
        self.width = width
        self.height = height

        self.camera_type = camera_type
        if camera_type not in ALLOWED_CAMERA_TYPES:
            raise ValueError(f"Camera type {camera_type} is not allowed. Allowed types are: {ALLOWED_CAMERA_TYPES}")
        if camera_type == "perspective":
            if any(n is None for n in (yfov, znear)):
                raise ValueError("Perspective camera needs to have yfov and znear defined.")
        self.aspect_ratio = aspect_ratio
        self.yfov = yfov
        self.zfar = zfar
        self.znear = znear
        self.xmag = xmag
        self.ymag = ymag

    @property
    def observation_space(self):
        return spaces.Box(low=0, high=255, shape=[3, self.height, self.width], dtype=np.uint8)

    def copy(self, with_children=True, **kwargs):
        """Return a copy of the Camera with copy of the children attached to the copy."""

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1

        instance_copy = type(self)(
            name=copy_name,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
            collider=self.collider,
            width=self.width,
            height=self.height,
            aspect_ratio=self.aspect_ratio,
            yfov=self.yfov,
            zfar=self.zfar,
            znear=self.znear,
            camera_type=self.camera_type,
            xmag=self.xmag,
            ymag=self.ymag,
        )

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children
            for child in instance_copy.tree_children:
                child._post_copy()

        return instance_copy


class CameraDistant(Camera):
    """A Distant Camera looking at the origin.

    The Distant Camera is identical to the Camera but override the default position and rotation to be located
    slightly away from the origin along the z axis and look toward the origin.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        width=256,
        height=256,
        aspect_ratio: Optional[float] = None,
        yfov: Optional[float] = 60,
        znear: Optional[float] = 0.3,
        zfar: Optional[float] = None,
        camera_type: Optional[str] = "perspective",
        xmag: Optional[float] = None,
        ymag: Optional[float] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        collider: Optional[Collider] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):

        if position is None:
            position = [0.0, 0.0, -10.0]
        if rotation is None:
            rotation = [0.0, 1.0, 0.0, 0.0]

        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            collider=collider,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            yfov=yfov,
            zfar=zfar,
            znear=znear,
            camera_type=camera_type,
            xmag=xmag,
            ymag=ymag,
        )
