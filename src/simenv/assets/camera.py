from .asset import Asset


class Camera(Asset):
    dimensionality = 3
    def __init__(self, name="Camera", translation=[0, 2, -5], rotation=[0, 0, 0, 1], width=256, height=256, parent=None, children=None):
        super().__init__(name=name, translation=translation, rotation=rotation, scale=None, parent=parent, children=children)
        self.width = width
        self.height = height
