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
""" A simulate Camera."""
import itertools
from typing import Any, List, Optional, Union

import numpy as np

from ..utils import logging
from .asset import Asset


logger = logging.get_logger(__name__)

try:
    from gym import spaces
except ImportError:
    from . import spaces

    # Our implementation of gym space classes if gym is not installed
    logger.warning(
        "The gym library is not installed, falling back our implementation of gym.spaces. "
        "To remove this message pip install simulate[rl]"
    )


ALLOWED_CAMERA_TYPES = ["perspective", "orthographic"]


class Camera(Asset):
    """
    A Camera asset.
    This Camera is located at the origin by default and has no rotation.

    Args:
        width (`int`, *optional*, defaults to `256`):
            The width of the Camera. Default: 256
        height (`int`, *optional*, defaults to `256`):
            The height of the Camera. Default: 256
        camera_type (`str`, *optional*, defaults to `perspective`):
            The type of camera. Can be one of:
            [
                "perspective",
                "orthographic"
            ]
        znear (`float`, *optional*, defaults to `0.3`):
            The near clipping plane of the Camera.
        yfov (`float` or `np.ndarray`, *optional*, defaults to `60`):
            The vertical field of view of the Camera in degrees.
        aspect_ratio (`float`, *optional*, defaults to `None`):
            The aspect ratio of the Camera if needed
        zfar (`float`, *optional*, defaults to `None`):
            The far clipping plane of the Camera.
        xmag (`float`, *optional*, defaults to `None`):
            The x magnification of the Camera.
        ymag (`float`, *optional*, defaults to `None`):
            The y magnification of the Camera.
        name (`str`, *optional*, defaults to `None`):
            The name of the Camera.
        sensor_tag (`str`, *optional*, defaults to `CameraSensor`):
            The tag of the Camera.
        position (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the Camera.
        rotation (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The rotation of the Camera.
        scaling (`float` or `List[float]`, *optional*, defaults to `1.0`):
            The scaling of the Camera.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the Camera is an actor.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the Camera.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the Camera.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        width: int = 256,
        height: int = 256,
        camera_type: str = "perspective",
        znear: float = 0.3,
        yfov: Optional[Union[float, np.ndarray]] = 60,
        aspect_ratio: Optional[float] = None,
        zfar: Optional[float] = None,
        xmag: Optional[float] = None,
        ymag: Optional[float] = None,
        name: Optional[str] = None,
        sensor_tag: str = "CameraSensor",
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        is_actor: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[List["Asset"]] = None,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            is_actor=is_actor,
            parent=parent,
            children=children,
        )
        self.width = width
        self.height = height

        self.camera_type = camera_type
        self.sensor_tag = sensor_tag
        if camera_type not in ALLOWED_CAMERA_TYPES:
            raise ValueError(f"Camera type {camera_type} is not allowed. Allowed types are: {ALLOWED_CAMERA_TYPES}")
        if camera_type == "perspective":
            if any(n is None for n in (yfov, znear)):
                raise ValueError("Perspective camera needs to have yfov and znear defined.")
        elif camera_type == "orthographic":
            if any(n is None for n in (xmag, ymag, znear, zfar)):
                raise ValueError("Orthographic camera needs to have xmag, ymag, znear and zfar defined.")

        self.aspect_ratio = aspect_ratio
        self.yfov = yfov
        self.zfar = zfar
        self.znear = znear
        self.xmag = xmag
        self.ymag = ymag

    @property
    def observation_space(self) -> spaces.Box:
        """
        Get the observation space of the Camera.

        Returns:
            observation (`spaces.Box`):
                The observation space of the Camera.
        """
        return spaces.Box(low=0, high=255, shape=[3, self.height, self.width], dtype=np.uint8)

    def copy(self, with_children: bool = True, **kwargs: Any):
        """
        Make a copy of the Camera with copy of the children attached to the copy.

        Args:
            with_children (`bool`, *optional*, defaults to `True`):
                Whether to copy the children of the Camera.
        """

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1

        instance_copy = type(self)(
            name=copy_name,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
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
    """
    A Distant Camera looking at the origin.

    The Distant Camera is identical to the Camera but override the default position and rotation to be located
    slightly away from the origin along the z axis and look toward the origin.

    Args:
        width (`int`, *optional*, defaults to `256`):
            The width of the Camera.
        height (`int`, *optional*, defaults to `256`):
            The height of the Camera.
        aspect_ratio (`float`, *optional*, defaults to `None`):
            The aspect ratio of the Camera if needed
        yfov (`float` or `np.ndarray`, *optional*, defaults to `60`):
            The vertical field of view of the Camera in degrees.
        znear (`float`, *optional*, defaults to `0.3`):
            The near clipping plane of the Camera.
        zfar (`float`, *optional*, defaults to `None`):
            The far clipping plane of the Camera.
        camera_type (`str`, *optional*, defaults to `perspective`):
            The type of the Camera. Can be one of:
            [
                `perspective`,
                `orthographic`,
            ]
        xmag (`float`, *optional*, defaults to `None`):
            The horizontal magnification of the Camera.
        ymag (`float`, *optional*, defaults to `None`):
            The vertical magnification of the Camera.
        name (`str`, *optional*, defaults to `None`):
            The name of the Camera.
        sensor_tag (`str`, *optional*, defaults to `CameraSensor`):
            The tag of the Camera.
        position (`List[float]`, *optional*, defaults to `[0.0, 5.0, -10.0]`):
            The position of the Camera.
        rotation (`List[float]`, *optional*, defaults to `[0.0, 1.0, 0.0, 0.0]`):
            The rotation of the Camera.
        scaling (`float` or `List[float]`, *optional*, defaults to `1.0`):
            The scaling of the Camera.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the Camera is an actor.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the Camera.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the Camera.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        width: int = 256,
        height: int = 256,
        aspect_ratio: Optional[float] = None,
        yfov: float = 60,
        znear: float = 0.3,
        zfar: Optional[float] = None,
        camera_type: str = "perspective",
        xmag: Optional[float] = None,
        ymag: Optional[float] = None,
        name: Optional[str] = None,
        sensor_tag: str = "CameraSensor",
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        is_actor: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[List["Asset"]] = None,
    ):

        if position is None:
            position = [0.0, 5.0, -10.0]
        if rotation is None:
            rotation = [0.0, 1.0, 0.0, 0.0]

        super().__init__(
            name=name,
            sensor_tag=sensor_tag,
            position=position,
            rotation=rotation,
            scaling=scaling,
            is_actor=is_actor,
            parent=parent,
            children=children,
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
