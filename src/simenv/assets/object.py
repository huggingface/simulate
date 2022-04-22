from .asset import Asset


class Object(Asset):
    dimensionality = 3
    dynamic = False

    def __init__(
        self, name, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1], parent=None, children=None
    ):
        super().__init__(
            name, translation=translation, rotation=rotation, scale=scale, parent=parent, children=children
        )


class Primitive(Object):
    dynamic = True
    pass


class Sphere(Primitive):
    pass


class Capsule(Primitive):
    pass


class Cylinder(Primitive):
    pass


class Cube(Primitive):
    pass


class Plane(Primitive):
    pass


class Quad(Primitive):
    pass
