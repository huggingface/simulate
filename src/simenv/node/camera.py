from simenv.core import Node


class Camera(Node):
    def __init__(self, name, translation=[0, 2, -5], rotation=[0, 0, 0, 1], width=256, height=256):
        super().__init__(name, translation, rotation)
        self.width = width
        self.height = height
