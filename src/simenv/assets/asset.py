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
import math
import uuid
from typing import Optional, Sequence, Union

import numpy as np

from .anytree import NodeMixin
from .utils import camelcase_to_snakecase, get_transform_from_trs, quat_from_euler


class Asset(NodeMixin, object):
    dimensionality = 3  # 2 for bi-dimensional assets and 3 for tri-dimensional assets (default is 3)
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name=None,
        center=None,
        direction=None,
        scale=None,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):
        self.id = next(self.__class__.__NEW_ID)
        if name is None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{self.id:02d}")
        self.name = name

        self.tree_parent = parent
        if children:
            self.tree_children = children

        self._center = None
        self._direction = None
        self._scale = None
        self._transform = None
        self.center = center
        self.direction = direction
        self.scale = scale

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0]
            elif len(value) != 3:
                raise ValueError("Center should be of size 3 (X, Y, Z)")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transform_matrix = None  # Reset transform matrix
        self._center = np.array(value)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [1.0, 0.0, 0.0, 0.0]
            elif len(value) == 3:
                value = quat_from_euler(*value)
            elif len(value) != 4:
                raise ValueError("Direction should be of size 3 (Euler angles) or 4 (Quaternions")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transform_matrix = None  # Reset transform matrix
        self._direction = np.array(value)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [1.0, 1.0, 1.0]
            elif len(value) == 1:
                value = [value, value, value]
            elif len(value) != 3:
                raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transform_matrix = None  # Reset transform matrix
        self._scale = np.array(value)

    @property
    def transform(self):
        if self._transform is None:
            self._transform = get_transform_from_trs(self.center, self.direction, self.scale)
        return self._transform

    @transform.setter
    def transform(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transform = np.array(value)
        self._center = None  # Reset center/direction/scale
        self._direction = None  # Not sure we can extract center/direction/scale from transform matrix in a unique way
        self._scale = None
