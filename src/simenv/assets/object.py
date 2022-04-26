from typing import List, Optional

from trimesh import Trimesh

from .asset import Asset


class Object(Asset):
    dimensionality = 3
    dynamic = False

    def __init__(
        self,
        name: Optional[str] = None,
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        mesh: Optional[Trimesh] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(
            name=name, translation=translation, rotation=rotation, scale=scale, parent=parent, children=children
        )
        self.mesh = mesh

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__} - Mesh={self.mesh})"


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
