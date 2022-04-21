from simenv.core import Node


class Object(Node):
    def __init__(self, name, dynamic, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        super().__init__(name, translation, rotation, scale)
        self.dynamic = dynamic
