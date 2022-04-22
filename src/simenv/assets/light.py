from .asset import Asset


class Light(Asset):
    dimensionality = 3

    def __init__(self, name, type, intensity=1, translation=[0, 0, 0], rotation=[0, 0, 0, 1]):
        super().__init__(name, translation, rotation)
        self.type = type
        self.intensity = intensity


class SpotLight(Light):
    def __init__(self, name, intensity=1, translation=[0, 0, 0], rotation=[0, 0, 0, 1]):
        type = 0
        super().__init__(name, type, intensity, translation, rotation)


class DirectionalLight(Light):
    def __init__(self, name, intensity=1, translation=[0, 0, 0], rotation=[0, 0, 0, 1]):
        type = 1
        super().__init__(name, type, intensity, translation, rotation)


class PointLight(Light):
    def __init__(self, name, intensity=1, translation=[0, 0, 0], rotation=[0, 0, 0, 1]):
        type = 2
        super().__init__(name, type, intensity, translation, rotation)
