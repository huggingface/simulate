import itertools
from typing import Any, List, Optional, Union

import numpy as np

from .asset import Asset


class Light(Asset):
    """A Scene Light.

    Three type of punctual lights are implemented:
    - directional (default): an infinitely distant point source
    - positional: point sources located in the real-world.
        A cone angle can be defined to limit the spatial distribution of a positional light beam in which case
        these are often known as spotlight. a Value of None or above 90 degree means no spatial limitation.

    Punctual lights are defined as infinitely small points that emit light in well-defined directions and intensities.

    Angles are in degrees.

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
        """Return a copy of the Asset. Parent and children are not attached to the copy."""
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
    """A Sun-like scene Light

    Override the default properties of the Light class to get a distant light coming from an angle.
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
