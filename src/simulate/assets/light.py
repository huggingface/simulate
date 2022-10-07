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
import itertools
from typing import Any, List, Optional, Union

import numpy as np

from .asset import Asset


class Light(Asset):
    """
    A Scene Light.
    Punctual lights are defined as infinitely small points that emit light in well-defined directions and intensities.
    Angles are in degrees.

    Args:
        intensity (`float`, *optional*, defaults to `1.0`):
            The intensity of the light.
        color (`List[float]`, *optional*, defaults to `[1.0, 1.0, 1.0]`):
            The color of the light.
        range (`float`, *optional*, defaults to `None`):
            The range of the light.
        inner_cone_angle (`float` or `np.ndarray`, *optional*, defaults to `0.0`):
            The inner cone angle of the light.
        outer_cone_angle (`float` or `np.ndarray`, *optional*, defaults to `45.0`):
            The outer cone angle of the light.
        light_type (`str`, *optional*, defaults to `"directional"`):
            The type of the light. 2 types of punctual lights are implemented:
            - `"directional"`: an infinitely distant point source
            - `"positional"`: point sources located in the real-world.
            A cone angle can be defined to limit the spatial distribution of a positional light beam in which case
            these are often known as spotlight. a Value of None or above 90 degree means no spatial limitation.
        name (`str`, *optional*, defaults to `None`):
            The name of the light.
        position (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the light.
        rotation (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The rotation of the light.
        scaling (`float` or `List[float]`, *optional*, defaults to `1.0`):
            The scaling of the light.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the light is an actor.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the light.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the light.
    """

    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        intensity: float = 1.0,
        color: Optional[List[float]] = None,
        range: Optional[float] = None,
        inner_cone_angle: Union[float, np.ndarray] = 0.0,
        outer_cone_angle: Union[float, np.ndarray] = 45.0,
        light_type: str = "directional",
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        is_actor: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[List["Asset"]] = None,
    ):
        if color is None:
            color = [1.0, 1.0, 1.0]
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            is_actor=is_actor,
            parent=parent,
            children=children,
        )
        self.intensity = intensity
        self.color = color
        self.range = range

        if light_type not in ["directional", "positional"]:
            raise ValueError("Light type should be selected in ['directional', 'positional']")
        self.light_type = light_type
        self.inner_cone_angle = inner_cone_angle
        self.outer_cone_angle = outer_cone_angle

    def copy(self, with_children: bool = True, **kwargs: Any) -> "Light":
        """
        Make a copy of the Asset.

        Args:
            with_children (`bool`, *optional*, defaults to `True`):
                Whether to copy the children of the asset.

        Returns:
            copy (`Light`):
                The copy of the asset.
        """
        instance_copy = type(self)(
            name=None,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
            intensity=self.intensity,
            color=self.color,
            range=self.range,
            light_type=self.light_type,
            inner_cone_angle=self.inner_cone_angle,
            outer_cone_angle=self.outer_cone_angle,
        )

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children

        return instance_copy


class LightSun(Light):
    """
    A Sun-like scene Light
    Override the default properties of the Light class to get a distant light coming from an angle.

    Args:
        intensity (`float`, *optional*, defaults to `1.0`):
            The intensity of the light.
        color (`List[float]`, *optional*, defaults to `[1.0, 1.0, 1.0]`):
            The color of the light.
        range (`float`, *optional*, defaults to `None`):
            The range of the light.
        inner_cone_angle (`float` or `np.ndarray`, *optional*, defaults to `0.0`):
            The inner cone angle of the light.
        outer_cone_angle (`float` or `np.ndarray`, *optional*, defaults to `45.0`):
            The outer cone angle of the light.
        light_type (`str`, *optional*, defaults to `"directional"`):
            The type of the light. 2 types of punctual lights are implemented:
            - `"directional"`: an infinitely distant point source
            - `"positional"`: point sources located in the real-world.
            A cone angle can be defined to limit the spatial distribution of a positional light beam in which case
            these are often known as spotlight. a Value of None or above 90 degree means no spatial limitation.
        name (`str`, *optional*, defaults to `None`):
            The name of the light.
        position (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the light.
        rotation (`List[float]`, *optional*, defaults to `[-60, 225, 0]`):
            The rotation of the light.
        scaling (`float` or `List[float]`, *optional*, defaults to `1.0`):
            The scaling of the light.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the light is an actor.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the light.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the light.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        intensity: float = 1.0,
        color: Optional[List[float]] = None,
        range: Optional[float] = None,
        inner_cone_angle: float = 0.0,
        outer_cone_angle: float = 45.0,
        light_type: str = "directional",
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        is_actor: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[List["Asset"]] = None,
    ):
        if color is None:
            color = [1.0, 1.0, 1.0]
        if rotation is None:
            rotation = [-60, 225, 0]

        super().__init__(
            intensity=intensity,
            color=color,
            range=range,
            inner_cone_angle=inner_cone_angle,
            outer_cone_angle=outer_cone_angle,
            light_type=light_type,
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            is_actor=is_actor,
            parent=parent,
            children=children,
        )
