# Copyright 2022 The HuggingFace Simenv Authors.
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
"""Utilities."""
import itertools
import math
import re
from typing import List, Union

import numpy as np


_uppercase_uppercase_re = re.compile(r"([A-Z]+)([A-Z][a-z])")
_lowercase_uppercase_re = re.compile(r"([a-z\d])([A-Z])")

_single_underscore_re = re.compile(r"(?<!_)_(?!_)")
_multiple_underscores_re = re.compile(r"(_{2,})")

_split_re = r"^\w+(\.\w+)*$"


def make_default_name_for_object(obj):
    id = next(obj.__class__.__NEW_ID)
    name = camelcase_to_snakecase(obj.__class__.__name__ + f"_{id:02d}")
    return name


def camelcase_to_snakecase(name: str) -> str:
    """Convert camel-case string to snake-case."""
    name = _uppercase_uppercase_re.sub(r"\1_\2", name)
    name = _lowercase_uppercase_re.sub(r"\1_\2", name)
    return name.lower()


def snakecase_to_camelcase(name: str) -> str:
    """Convert snake-case string to camel-case string."""
    name = _single_underscore_re.split(name)
    name = [_multiple_underscores_re.split(n) for n in name]
    return "".join(n.capitalize() for n in itertools.chain.from_iterable(name) if n != "")


def get_transform_from_trs(
    translation: Union[np.ndarray, List[float]],
    rotation: Union[np.ndarray, List[float]],
    scale: Union[np.ndarray, List[float]],
) -> np.ndarray:
    """Create a homogenious transform matrix (4x4) from 3D vector of translation and scale, and a quaternion vector of rotation."""
    if translation is None or rotation is None or scale is None:
        return None

    if not isinstance(translation, np.ndarray):
        translation = np.array(translation)
    if not isinstance(rotation, np.ndarray):
        rotation = np.array(rotation)
    if not isinstance(scale, np.ndarray):
        scale = np.array(scale)

    translation = np.squeeze(translation)
    rotation = np.squeeze(rotation)
    scale = np.squeeze(scale)

    if not translation.shape == (3,):
        raise ValueError("The translation vector should be of size 3")
    if not rotation.shape == (4,):
        raise ValueError("The rotation vector should be of size 4")
    if not scale.shape == (3,):
        raise ValueError("The scale vector should be of size 3")

    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = translation
    translation_matrix[3, 3] = 1

    # Rotation matrix
    qx, qy, qz, qw = rotation[0], rotation[1], rotation[2], rotation[3]
    r00 = 1 - 2 * (qy * qy + qz * qz)
    r01 = 2 * (qx * qy - qw * qz)
    r02 = 2 * (qx * qz + qw * qy)

    r10 = 2 * (qx * qy + qw * qz)
    r11 = 1 - 2 * (qx * qx + qz * qz)
    r12 = 2 * (qy * qz - qw * qx)

    r20 = 2 * (qx * qz - qw * qy)
    r21 = 2 * (qy * qz + qw * qx)
    r22 = 1 - 2 * (qx * qx + qy * qy)
    # Gather it all
    rotation_matrix = np.zeros((4, 4))
    rotation_matrix[3, 3] = 1
    rotation_matrix[:3, :3] = np.array([[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]])

    scale_matrix = np.zeros((4, 4))
    scale_matrix[0, 0] = scale[0]
    scale_matrix[1, 1] = scale[1]
    scale_matrix[2, 2] = scale[2]
    scale_matrix[3, 3] = 1

    transformation_matrix = translation_matrix @ rotation_matrix @ scale_matrix
    return transformation_matrix


def get_product_of_quaternions(q: Union[np.ndarray, List[float]], r: Union[np.ndarray, List[float]]) -> np.ndarray:
    qx, qy, qz, qw = q[0], q[1], q[2], q[3]
    rx, ry, rz, rw = r[0], r[1], r[2], r[3]
    return np.array(
        [
            rw * qx + rx * qw - ry * qz + rz * qy,
            rw * qy + rx * qz + ry * qw - rz * qx,
            rw * qz - rx * qy + ry * qx + rz * qw,
            rw * qw - rx * qx - ry * qy - rz * qz,
        ]
    )


def quat_from_euler(x: float, y: float, z: float) -> List[float]:
    qx = np.sin(x / 2) * np.cos(y / 2) * np.cos(z / 2) - np.cos(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    qy = np.cos(x / 2) * np.sin(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.cos(y / 2) * np.sin(z / 2)
    qz = np.cos(x / 2) * np.cos(y / 2) * np.sin(z / 2) - np.sin(x / 2) * np.sin(y / 2) * np.cos(z / 2)
    qw = np.cos(x / 2) * np.cos(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    return [qx, qy, qz, qw]


def quat_from_degrees(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))


def degrees_to_radians(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))
