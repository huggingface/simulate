from simenv.node.object import Object


class Primitive(Object):
    def __init__(self, name, dynamic, primitive_type, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        super().__init__(name, dynamic, translation, rotation, scale)
        self.primitive_type = primitive_type


class Sphere(Primitive):
    def __init__(self, name, dynamic=True, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 0
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)


class Capsule(Primitive):
    def __init__(self, name, dynamic=True, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 1
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)


class Cylinder(Primitive):
    def __init__(self, name, dynamic=True, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 2
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)


class Cube(Primitive):
    def __init__(self, name, dynamic=True, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 3
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)


class Plane(Primitive):
    def __init__(self, name, dynamic=False, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 4
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)


class Quad(Primitive):
    def __init__(self, name, dynamic=False, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        primitive_type = 5
        super().__init__(name, dynamic, primitive_type, translation, rotation, scale)
