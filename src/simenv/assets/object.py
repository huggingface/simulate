from optparse import Option
import itertools
from typing import List, Optional, Union

import trimesh

from .asset import Asset


class Object(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name: Optional[str] = None,
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        mesh: Optional[trimesh.Trimesh] = None,
        dynamic: bool = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(
            name=name, translation=translation, rotation=rotation, scale=scale, parent=parent, children=children
        )
        self.mesh = mesh
        self.dynamic = dynamic

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__} - Mesh={self.mesh})"


class Sphere(Object):
    """
    An isosphere or a UV sphere (latitude + longitude).
    """
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name: Optional[str] = None,
        radius: Optional[float] = 1.0,
        subdivisions: Optional[int] = None,
        count: Optional[List[int]] = None,
        theta: Optional[List[float]] = None,
        phi: Optional[List[float]] = None,
        type: Optional[str] = "uv",
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if type == "uv":
            if subdivisions is not None:
                raise ValueError(
                    "You cannot use 'subdivisions' with a sphere of type 'uv'. "
                    "Specify the mesh with 'count', 'theta' or 'phi' or change the 'type' of the Sphere."
                )
            if count is None:
                count = [32, 32]
            mesh = trimesh.creation.uv_sphere(radius=radius, count=count, theta=theta, phi=phi)
        elif type == "iso":
            if count is not None or theta is not None or phi is not None:
                raise ValueError(
                    "You cannot use 'count', 'theta' or 'phi' with a sphere of type 'iso'. "
                    "Specify the mesh with 'subdivisions' instead or change the 'type' of the Sphere."
                )
            if subdivisions is None:
                subdivisions = 3
            mesh = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)
        else:
            raise ValueError("Sphere type should be one of 'uv' or 'iso'.")

        super().__init__(
            mesh=mesh,
            name=name,
            translation=translation,
            rotation=rotation,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Capsule(Object):
    """
    A capsule (a cylinder with hemispheric ends).

    Parameters
    ----------
    height : float
      Center to center distance of two spheres
    radius : float
      Radius of the cylinder and hemispheres
    count : (2,) int
      Number of sections on latitude and longitude

    Returns
    ----------
    capsule : trimesh.Trimesh
      Capsule geometry with:
        - cylinder axis is along Z
        - one hemisphere is centered at the origin
        - other hemisphere is centered along the Z axis at height
    """
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name: Optional[str] = None,
        height: Optional[float] = 1.0,
        radius: Optional[float] = 1.0,
        count: Optional[List[int]] = [32, 32],
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = trimesh.creation.capsule(height=height, radius=radius, count=count)
        super().__init__(
            mesh=mesh,
            name=name,
            translation=translation,
            rotation=rotation,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cylinder(Object):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    def __init__(
        self,
        name: Optional[str] = None,
        height: Optional[float] = 1.0,
        radius: Optional[float] = 1.0,
        sections: Optional[int] = 32,
        segment: Optional[List[float]] = None,
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections, segment=segment)
        super().__init__(
            mesh=mesh,
            name=name,
            translation=translation,
            rotation=rotation,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cube(Object):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    def __init__(
        self,
        name: Optional[str] = None,
        extents: Optional[Union[float, List[float]]] = None,
        translation: Optional[List[float]] = [0.0, 0.0, 0.0],
        rotation: Optional[List[float]] = [0.0, 0.0, 0.0, 1.0],
        scale: Optional[List[float]] = [1.0, 1.0, 1.0],
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = trimesh.creation.box(extents=extents)
        super().__init__(
            mesh=mesh,
            name=name,
            translation=translation,
            rotation=rotation,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )
