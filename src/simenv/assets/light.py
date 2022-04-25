from .asset import Asset


class Light(Asset):
    dimensionality = 3

    def __init__(self, name, type, intensity=1, color=[1.0, 1.0, 1.0], range=None, translation=[0, 0, 0], rotation=[0, 0, 0, 1]):
        super().__init__(name, translation, rotation)
        self.type = type
        self.intensity = intensity
        self.color = color
        self.range = range


class SpotLight(Light):
    pass

class DirectionalLight(Light):
    pass

class PointLight(Light):
    pass
