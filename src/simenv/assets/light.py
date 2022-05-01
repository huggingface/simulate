from typing import List, Optional
import itertools

from .asset import Asset


class Light(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name,
        intensity=1,
        color=[1.0, 1.0, 1.0],
        range=None,
        translation=[0, 0, 0],
        rotation=[0, 0, 0, 1],
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, translation=translation, rotation=rotation, parent=parent, children=children)

        self.intensity = intensity
        self.color = color
        self.range = range


class SpotLight(Light):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    pass


class DirectionalLight(Light):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    pass


class PointLight(Light):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    pass
