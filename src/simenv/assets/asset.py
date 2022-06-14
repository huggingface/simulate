# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" A simenv Asset - Objects in the scene (mesh, primitives, camera, lights)."""
import itertools
import uuid
from typing import List, Optional, Union

import numpy as np

from .anytree import NodeMixin
from .collider import Collider
from .utils import camelcase_to_snakecase, get_transform_from_trs, quat_from_euler


class Asset(NodeMixin, object):
    """Create an Asset in the Scene.

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    """

    dimensionality = 3  # 2 for bi-dimensional assets and 3 for tri-dimensional assets (default is 3)
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        transformation_matrix=None,
        collider: Optional[Collider] = None,
        parent=None,
        children=None,
    ):
        self._uuid = uuid.uuid4()
        id = next(self.__class__.__NEW_ID)
        if name is None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{id:02d}")
        self.name = name

        self.tree_parent = parent
        if children:
            self.tree_children = children

        self._position = None
        self._rotation = None
        self._scaling = None
        self._transformation_matrix = None
        self.position = position
        self.rotation = rotation
        self.scaling = scaling
        self.collider = collider
        if transformation_matrix is not None:
            self.transformation_matrix = transformation_matrix

    @property
    def uuid(self):
        """A unique identifier of the node if needed."""
        return self._uuid

    def get(self, name: str):
        """Return the first children tree node with the given name."""
        for node in self.tree_children:
            if node.name == name:
                return node

    def copy(self):
        """Return a copy of the Asset. Parent and children are not attached to the copy."""
        return Asset(name=None, position=self.position, rotation=self.rotation, scaling=self.scaling)

    def translate(self, vector: Optional[List[float]] = None):
        """Translate the asset from a given translation vector

        Parameters
        ----------
        vector : np.ndarray or list, optional
            Translation vector to apply to the object ``[x, y, z]``.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        if vector is None:
            return self
        self.position += np.array(vector)
        return self

    def translate_x(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``x`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``x`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((float(amount), 0.0, 0.0))
        return self

    def translate_y(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``y`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``y`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((0.0, float(amount), 0.0))
        return self

    def translate_z(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``z`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``z`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((0.0, 0.0, float(amount)))
        return self

    def rotate(self, rotation: Optional[List[float]] = None):
        """Rotate the asset with a given rotation quaternion.
        Use ``rotate_x``, ``rotate_y`` or ``rotate_z`` for simple rotations around a specific axis.

        Parameters
        ----------
        rotation : np.ndarray or list, optional
            Rotation quaternion to apply to the object ``[x, y, z, w]``.
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        if rotation is None:
            return self
        self.rotation = np.array(rotation) * self.rotation
        return self

    def _rotate_axis(self, vector: Optional[List[float]] = None, value: Optional[float] = None):
        """Helper to rotate around a single axis."""
        if value is None or vector is None:
            return self
        self.rotation = np.array(vector + [np.radians(value)]) * self.rotation
        return self

    def rotate_x(self, value: Optional[float] = None):
        """Rotate the asset around the ``x`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``x`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[1.0, 0.0, 0.0], value=value)

    def rotate_y(self, value: Optional[float] = None):
        """Rotate the asset around the ``y`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``y`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[0.0, 1.0, 0.0], value=value)

    def rotate_z(self, value: Optional[float] = None):
        """Rotate the asset around the ``z`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``z`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[0.0, 0.0, 1.0], value=value)

    def scale(self, scaling: Optional[Union[float, List[float]]] = None):
        """Scale the asset with a given scaling, either a global scaling value or a vector of ``[x, y, z]`` scaling values.
        Use ``scale_x``, ``scale_y`` or ``scale_z`` for simple scaling around a specific axis.

        Parameters
        ----------
        scaling : float or np.ndarray or list, optional
            Global scaling (float) or vector of  scaling values to apply to the object along the ``[x, y, z]`` axis.
            Default to applying no scaling.

        Returns
        -------
        self : Asset modified in-place with the scaling.

        Examples
        --------

        """
        if scaling is None:
            return self
        if scaling is None:
            scaling = [1.0, 1.0, 1.0]
        elif isinstance(scaling, (float, int)) or (isinstance(scaling, np.ndarray) and len(scaling) == 1):
            scaling = [scaling, scaling, scaling]
        elif len(scaling) != 3:
            raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
        self.scaling = np.multiply(self.scaling, scaling)
        return self

    # getters for position/rotation/scale

    @property
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    @property
    def scaling(self):
        return self._scaling

    @property
    def transformation_matrix(self):
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale

    @position.setter
    def position(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0]
            elif len(value) != 3:
                raise ValueError("position should be of size 3 (X, Y, Z)")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._position = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @rotation.setter
    def rotation(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0, 1.0]
            elif len(value) == 3:
                value = quat_from_euler(*value)
            elif len(value) != 4:
                raise ValueError("rotation should be of size 3 (Euler angles) or 4 (Quaternions")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._rotation = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @scaling.setter
    def scaling(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [1.0, 1.0, 1.0]
            elif len(value) == 1:
                value = [value, value, value]
            elif len(value) != 3:
                raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._scaling = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @transformation_matrix.setter
    def transformation_matrix(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transformation_matrix = np.array(value)

        # Not sure we can extract position/rotation/scale from transform matrix in a unique way
        # Reset position/rotation/scale
        self._position = None
        self._rotation = None
        self._scaling = None

        self._post_asset_modification()

    def _post_asset_modification(self):
        if getattr(self.tree_root, "engine", None) is not None and self.tree_root.tree_root.engine.auto_update:
            self.tree_root.engine.update_asset(self)

    def _post_attach_parent(self, parent):
        """NodeMixing nethod call after attaching to a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.update_asset(self)

    def _post_detach_parent(self, parent):
        """NodeMixing nethod call after detaching from a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.remove_asset(self)
