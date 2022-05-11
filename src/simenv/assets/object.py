import itertools
from optparse import Option
from typing import List, Optional, Union

import numpy as np
import pyvista as pv

from .asset import Asset


class Object3D(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        mesh: Optional[pv.UnstructuredGrid] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[Union[float, List[float]]] = None,
        dynamic: bool = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, center=center, direction=direction, scale=scale, parent=parent, children=children)
        self.mesh = mesh
        self.dynamic = dynamic

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__} - Mesh={self.mesh})"

    def plot(self, **kwargs):
        self.mesh.plot(**kwargs)


class Sphere(Asset):
    """Create a vtk Sphere

    Parameters
    ----------
    radius : float, optional
        Sphere radius.

    theta_resolution : int , optional
        Set the number of points in the longitude direction (ranging
        from ``start_theta`` to ``end_theta``).

    phi_resolution : int, optional
        Set the number of points in the latitude direction (ranging from
        ``start_phi`` to ``end_phi``).

    start_theta : float, optional
        Starting longitude angle.

    end_theta : float, optional
        Ending longitude angle.

    start_phi : float, optional
        Starting latitude angle.

    end_phi : float, optional
        Ending latitude angle.

    sphere_type : str, optional
        One of 'uv' for a UV-sphere or 'ico' for an icosphere.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        radius: Optional[float] = 1.0,
        theta_resolution: Optional[int] = 30,
        phi_resolution: Optional[int] = 30,
        start_theta: Optional[float] = 0,
        end_theta: Optional[float] = 360,
        start_phi: Optional[float] = 0,
        end_phi: Optional[float] = 180,
        sphere_type: Optional[str] = "uv",
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[Union[float, List[float]]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )
        if sphere_type not in ["uv", "ico"]:
            raise ValueError("Sphere type should be one of 'uv' or 'ico'.")

        from vtkmodules.vtkFiltersSources import vtkSphereSource

        sphere = vtkSphereSource()
        sphere.SetRadius(radius)
        sphere.SetThetaResolution(theta_resolution)
        sphere.SetPhiResolution(phi_resolution)
        sphere.SetStartTheta(start_theta)
        sphere.SetEndTheta(end_theta)
        sphere.SetStartPhi(start_phi)
        sphere.SetEndPhi(end_phi)
        sphere.SetLatLongTessellation(bool(sphere_type == "uv"))
        sphere.Update()
        self.mesh = pv.wrap(sphere.GetOutput())


class Capsule(Object3D):
    """
    A capsule (a cylinder with hemispheric ends).

    Parameters
    ----------
    height : float
      Center to center distance of two spheres
    radius : float
      Radius of the cylinder and hemispheres

    radius : float, optional
        Sphere radius.

    theta_resolution : int , optional
        Set the number of points in the longitude direction (ranging
        from ``start_theta`` to ``end_theta``).

    phi_resolution : int, optional
        Set the number of points in the latitude direction (ranging from
        ``start_phi`` to ``end_phi``).

    sphere_type : str, optional
        One of 'uv' for a UV-sphere or 'ico' for an icosphere.

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        height: Optional[float] = 1.0,
        radius: Optional[float] = 1.0,
        theta_resolution: Optional[int] = 30,
        phi_resolution: Optional[int] = 30,
        sphere_type: Optional[str] = "uv",
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[Union[float, List[float]]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if sphere_type not in ["uv", "ico"]:
            raise ValueError("Sphere type should be one of 'uv' or 'ico'.")

        from vtkmodules.vtkFiltersSources import vtkCapsuleSource

        capsule = vtkCapsuleSource()
        capsule.SetRadius(radius)
        capsule.SetCylinderLength(height)
        capsule.SetThetaResolution(theta_resolution)
        capsule.SetPhiResolution(phi_resolution)
        capsule.SetLatLongTessellation(bool(sphere_type == "uv"))
        capsule.Update()
        mesh = pv.wrap(capsule.GetOutput())
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cylinder(Object3D):
    """Create the surface of a cylinder.

    See also :func:`pyvista.CylinderStructured`.

    Parameters
    ----------
    radius : float, optional
        Radius of the cylinder.

    height : float, optional
        Height of the cylinder.

    resolution : int, optional
        Number of points on the circular face of the cylinder.

    capping : bool, optional
        Cap cylinder ends with polygons.  Default ``True``.

    Returns
    -------

    Examples
    --------
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        height: Optional[float] = 1.0,
        radius: Optional[float] = 1.0,
        resolution: Optional[int] = 32,
        capping: Optional[bool] = True,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Cylinder(radius=radius, height=height, resolution=resolution, capping=capping)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cube(Object3D):
    """Create a box with solid faces for the given bounds.

    Parameters
    ----------
    bounds : iterable, optional
        Specify the bounding box of the cube.
        ``(xMin, xMax, yMin, yMax, zMin, zMax)``.

    level : int, optional
        Level of subdivision of the faces.

    quads : bool, optional
        Flag to tell the source to generate either a quad or two
        triangle for a set of four points.  Default ``True``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        bounds: Optional[Union[float, List[float]]] = None,
        level: Optional[int] = 0,
        quads: Optional[bool] = True,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if isinstance(bounds, None):
            bounds = 1.0
        if isinstance(bounds, (float, int)):
            bounds = (-bounds, bounds, -bounds, bounds, -bounds, bounds)  # Make it a list
        mesh = pv.Box(bounds=bounds, level=level, quads=quads)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Plane(Object3D):
    """Create a plane.

    Parameters
    ----------
    i_size : float
        Size of the plane in the i direction.

    j_size : float
        Size of the plane in the j direction.

    i_resolution : int
        Number of points on the plane in the i direction.

    j_resolution : int
        Number of points on the plane in the j direction.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        i_size: Optional[float] = 1,
        j_size: Optional[float] = 1,
        i_resolution: Optional[int] = 10,
        j_resolution: Optional[int] = 10,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Plane(i_size=i_size, j_size=j_size, i_resolution=i_resolution, j_resolution=j_resolution)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Line(Object3D):
    """Create a line.

    Parameters
    ----------
    pointa : np.ndarray or list, optional
        Location in ``[x, y, z]``.

    pointb : np.ndarray or list, optional
        Location in ``[x, y, z]``.

    resolution : int, optional
        Number of pieces to divide line into.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        pointa: Optional[List[float]] = None,
        pointb: Optional[List[float]] = None,
        resolution: Optional[int] = 1,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if pointa is None:
            pointa = [-1.0, 0.0, 0.0]
        if pointb is None:
            pointb = [1.0, 0.0, 0.0]
        mesh = pv.Line(pointa=pointa, pointb=pointb, resolution=resolution)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class MultipleLines(Object3D):
    """Create multiple lines.

    Parameters
    ----------
    points : np.ndarray or list, optional
        List of points defining a broken line, default is ``[[-0.5, 0.0, 0.0], [0.5, 0.0, 0.0]]``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if points is None:
            points = [[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
        mesh = pv.MultipleLines(points=points)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Tube(Object3D):
    """Create a tube that goes from point A to point B.

    Parameters
    ----------
    pointa : np.ndarray or list, optional
        Location in ``[x, y, z]``.

    pointb : np.ndarray or list, optional
        Location in ``[x, y, z]``.

    resolution : int, optional
        Number of pieces to divide tube into.

    radius : float, optional
        Minimum tube radius (minimum because the tube radius may vary).

    n_sides : int, optional
        Number of sides for the tube.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        pointa: Optional[List[float]] = None,
        pointb: Optional[List[float]] = None,
        resolution: Optional[int] = 1,
        radius: Optional[float] = 1.0,
        n_sides: Optional[int] = 16,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if pointa is None:
            pointa = [-1.0, 0.0, 0.0]
        if pointb is None:
            pointb = [1.0, 0.0, 0.0]
        mesh = pv.Tube(pointa=pointa, pointb=pointb, radius=radius, resolution=resolution, n_sides=n_sides)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cube(Object3D):
    """Create a cube.

    It's possible to specify either the center and side lengths or
    just the bounds of the cube. If ``bounds`` are given, all other
    arguments are ignored.

    Parameters
    ----------
    x_length : float, optional
        Length of the cube in the x-direction.

    y_length : float, optional
        Length of the cube in the y-direction.

    z_length : float, optional
        Length of the cube in the z-direction.

    bounds : sequence, optional
        Specify the bounding box of the cube. If given, all other size
        arguments are ignored. ``(xMin, xMax, yMin, yMax, zMin, zMax)``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        x_length: Optional[float] = 1.0,
        y_length: Optional[float] = 1.0,
        z_length: Optional[float] = 1.0,
        bounds: Optional[List[float]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Cube(x_length=x_length, y_length=y_length, z_length=z_length, bounds=bounds)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cube(Object3D):
    """Create a cube.

    It's possible to specify either the center and side lengths or
    just the bounds of the cube. If ``bounds`` are given, all other
    arguments are ignored.

    Parameters
    ----------
    x_length : float, optional
        Length of the cube in the x-direction.

    y_length : float, optional
        Length of the cube in the y-direction.

    z_length : float, optional
        Length of the cube in the z-direction.

    bounds : sequence, optional
        Specify the bounding box of the cube. If given, all other size
        arguments are ignored. ``(xMin, xMax, yMin, yMax, zMin, zMax)``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        x_length: Optional[float] = 1.0,
        y_length: Optional[float] = 1.0,
        z_length: Optional[float] = 1.0,
        bounds: Optional[List[float]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Cube(x_length=x_length, y_length=y_length, z_length=z_length, bounds=bounds)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cube(Object3D):
    """Create a cube.

    It's possible to specify either the center and side lengths or
    just the bounds of the cube. If ``bounds`` are given, all other
    arguments are ignored.

    Parameters
    ----------
    x_length : float, optional
        Length of the cube in the x-direction.

    y_length : float, optional
        Length of the cube in the y-direction.

    z_length : float, optional
        Length of the cube in the z-direction.

    bounds : sequence, optional
        Specify the bounding box of the cube. If given, all other size
        arguments are ignored. ``(xMin, xMax, yMin, yMax, zMin, zMax)``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        x_length: Optional[float] = 1.0,
        y_length: Optional[float] = 1.0,
        z_length: Optional[float] = 1.0,
        bounds: Optional[List[float]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Cube(x_length=x_length, y_length=y_length, z_length=z_length, bounds=bounds)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Cone(Object3D):
    """Create a cone.

    Parameters
    ----------
    height : float, optional
        Height along the cone in its specified direction.

    radius : float, optional
        Base radius of the cone.

    resolution : int, optional
        Number of facets used to represent the cone.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        height: Optional[float] = 1.0,
        radius: Optional[float] = 1.0,
        resolution: Optional[int] = 6,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Cone(height=height, radius=radius, resolution=resolution)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Polygon(Object3D):
    """Create a polygon.

    Parameters
    ----------
    radius : float, optional
        The radius of the polygon.

    n_sides : int, optional
        Number of sides of the polygon.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        radius: Optional[float] = 1.0,
        n_sides: Optional[int] = 6,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Polygon(radius=radius, n_sides=n_sides)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Disc(Object3D):
    """Create a polygonal disk with a hole in the center.

    The disk has zero height. The user can specify the inner and outer
    radius of the disk, and the radial and circumferential resolution
    of the polygonal representation.

    Parameters
    ----------
    inner : float, optional
        The inner radius.

    outer : float, optional
        The outer radius.

    r_res : int, optional
        Number of points in radial direction.

    c_res : int, optional
        Number of points in circumferential direction.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        inner: Optional[
            float
        ] = 0.25,  # TODO(thomas) add back center and normal and see how to handle that for 2D/3D stuff
        outer: Optional[float] = 0.5,
        r_res: Optional[int] = 1,
        c_res: Optional[int] = 6,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Disc(inner=inner, outer=outer, r_res=r_res, c_res=c_res)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Text3D(Object3D):
    """Create 3D text from a string.

    Parameters
    ----------
    string : str
        String to generate 3D text from.

    depth : float, optional
        Depth of the text.  Defaults to ``0.5``.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        string: Optional[str] = "Hello",
        depth: Optional[float] = 0.5,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Text3D(string=string, depth=depth)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Triangle(Object3D):
    """Create a triangle defined by 3 points.

    Parameters
    ----------
    points : sequence, optional
        Points of the triangle.  Defaults to a right isosceles
        triangle (see example).

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Triangle(points=points)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Rectangle(Object3D):
    """Create a rectangle defined by 4 points.

    Parameters
    ----------
    points : sequence, optional
        Points of the rectangle.  Defaults to a simple example.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Rectangle(points=points)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class Circle(Object3D):
    """Create a single PolyData circle defined by radius in the XY plane.

    Parameters
    ----------
    radius : float, optional
        Radius of circle.

    resolution : int, optional
        Number of points on the circle.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        radius: Optional[float] = 0.5,
        resolution: Optional[int] = 100,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        mesh = pv.Circle(radius=radius, resolution=resolution)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )


class StructuredGrid(Object3D):
    """Create a single PolyData circle defined by radius in the XY plane.

    Parameters
    ----------
    x : np.ndarray or python list of list of floats
        Position of the points in x direction.

    y : np.ndarray or python list of list of floats
        Position of the points in y direction.

    z : np.ndarray or python list of list of floats
        Position of the points in z direction.

    Returns
    -------

    Examples
    --------

    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        x: Union[np.ndarray, List[List[float]]] = None,
        y: Union[np.ndarray, List[List[float]]] = None,
        z: Union[np.ndarray, List[List[float]]] = None,
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        dynamic: Optional[bool] = False,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)
        if not isinstance(z, np.ndarray):
            z = np.array(z)
        mesh = pv.StructuredGrid(x, y, z)
        super().__init__(
            mesh=mesh,
            name=name,
            center=center,
            direction=direction,
            scale=scale,
            dynamic=dynamic,
            parent=parent,
            children=children,
        )
