from typing import List, Optional

from .asset import Asset


class Light(Asset):
    dimensionality = 3

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
    pass


class DirectionalLight(Light):
    pass


class PointLight(Light):
    pass
