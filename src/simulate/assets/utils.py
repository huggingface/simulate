# Copyright 2022 The HuggingFace Simulate Authors.
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
import re
from typing import List, Optional, Tuple, Union

import numpy as np


_uppercase_uppercase_re = re.compile(r"([A-Z]+)([A-Z][a-z])")
_lowercase_uppercase_re = re.compile(r"([a-z\d])([A-Z])")

_single_underscore_re = re.compile(r"(?<!_)_(?!_)")
_multiple_underscores_re = re.compile(r"(_{2,})")


def camelcase_to_snakecase(name: str) -> str:
    """
    Convert camel-case string to snake-case.

    Args:
        name (`str`):
            The camel-case string to convert.

    Returns:
        name (`str`):
            The snake-case string.
    """
    name = _uppercase_uppercase_re.sub(r"\1_\2", name)
    name = _lowercase_uppercase_re.sub(r"\1_\2", name)
    return name.lower()


def snakecase_to_camelcase(name: str) -> str:
    """
    Convert snake-case string to camel-case string.

    Args:
        name (`str`):
            The snake-case string to convert.

    Returns:
        name (`str`):
            The camel-case string.
    """
    name = _single_underscore_re.split(name)
    name = [_multiple_underscores_re.split(n) for n in name]
    return "".join(n.capitalize() for n in itertools.chain.from_iterable(name) if n != "")


def get_transform_from_trs(
    translation: Union[np.ndarray, List[float]],
    rotation: Union[np.ndarray, List[float]],
    scale: Union[np.ndarray, List[float]],
) -> Optional[np.ndarray]:
    """
    Create a homogeneous transform matrix (4x4) from 3D vector of translation and scale,
    and a quaternion vector of rotation.

    Args:
        translation (`np.ndarray` or `list`):
            The translation vector.
        rotation (`np.ndarray` or `list`):
            The rotation quaternion.
        scale (`np.ndarray` or `list`):
            The scale vector.

    Returns:
        transform (`np.ndarray`):
            The homogeneous transform matrix.
    """
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
        raise ValueError("The rotation quaternions should be of size 4")
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


def get_trs_from_transform_matrix(transform_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get the translation, rotation and scale from a homogeneous transform matrix.

    Args:
        transform_matrix (`np.ndarray`):
            The homogeneous transform matrix.

    Returns:
        translation (`np.ndarray`):
            The translation vector.
        rotation (`np.ndarray`):
            The rotation quaternion.
        scale (`np.ndarray`):
            The scale vector.
    """
    if not transform_matrix.shape == (4, 4):
        raise ValueError("The transform matrix should be of size 4x4")

    # See https://math.stackexchange.com/questions/237369/given-this-transformation-matrix-how-do-i-decompose-it-into-translation-rotati

    translation = transform_matrix[:3, 3]
    scale = np.array(
        [
            np.linalg.norm(transform_matrix[:3, 0]),
            np.linalg.norm(transform_matrix[:3, 1]),
            np.linalg.norm(transform_matrix[:3, 2]),
        ]
    )

    rotation = np.zeros((3, 3))
    rotation[:, 0] = transform_matrix[:3, 0] / scale[0]
    rotation[:, 1] = transform_matrix[:3, 1] / scale[1]
    rotation[:, 2] = transform_matrix[:3, 2] / scale[2]

    m00, m01, m02 = rotation[0].tolist()
    m10, m11, m12 = rotation[1].tolist()
    m20, m21, m22 = rotation[2].tolist()

    # See https://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/

    tr = m00 + m11 + m22

    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2  # s=4*qw
        qw = 0.25 * s
        qx = (m21 - m12) / s
        qy = (m02 - m20) / s
        qz = (m10 - m01) / s
    elif (m00 > m11) and (m00 > m22):
        s = np.sqrt(1.0 + m00 - m11 - m22) * 2  # s=4*qx
        qw = (m21 - m12) / s
        qx = 0.25 * s
        qy = (m01 + m10) / s
        qz = (m02 + m20) / s
    elif m11 > m22:
        s = np.sqrt(1.0 + m11 - m00 - m22) * 2  # s=4*qy
        qw = (m02 - m20) / s
        qx = (m01 + m10) / s
        qy = 0.25 * s
        qz = (m12 + m21) / s
    else:
        s = np.sqrt(1.0 + m22 - m00 - m11) * 2  # s=4*qz
        qw = (m10 - m01) / s
        qx = (m02 + m20) / s
        qy = (m12 + m21) / s
        qz = 0.25 * s

    rotation = np.array([qx, qy, qz, qw])

    return translation, rotation, scale


def get_product_of_quaternions(q: Union[np.ndarray, List[float]], r: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Compute the product of two quaternions.

    Args:
        q (`np.ndarray` or `list`):
            The first quaternion.
        r (`np.ndarray` or `list`):
            The second quaternion.

    Returns:
        product (`np.ndarray`):
            The product of the two quaternions.
    """
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


def rotation_from_euler_radians(x: float, y: float, z: float) -> List[float]:
    """
    Return a rotation quaternion from Euler angles in radians.

    Args:
        x (`float`):
            The rotation in radians around the x-axis.
        y (`float`):
            The rotation in radians around the y-axis.
        z (`float`):
            The rotation in radians around the z-axis.

    Returns:
        rotation (`list`):
            The rotation quaternion.
    """
    qx = np.sin(x / 2) * np.cos(y / 2) * np.cos(z / 2) - np.cos(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    qy = np.cos(x / 2) * np.sin(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.cos(y / 2) * np.sin(z / 2)
    qz = np.cos(x / 2) * np.cos(y / 2) * np.sin(z / 2) - np.sin(x / 2) * np.sin(y / 2) * np.cos(z / 2)
    qw = np.cos(x / 2) * np.cos(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    return [qx, qy, qz, qw]


def rotation_from_euler_degrees(x: float, y: float, z: float) -> List[float]:
    """
    Return a rotation Quaternion from Euler angles in degrees.

    Args:
        x (`float`):
            The rotation in degrees around the x-axis.
        y (`float`):
            The rotation in degrees around the y-axis.
        z (`float`):
            The rotation in degrees around the z-axis.

    Returns:
        rotation (`list`):
            The rotation quaternion.
    """
    return rotation_from_euler_radians(np.radians(x), np.radians(y), np.radians(z))


def euler_from_quaternion(quaternion: Union[np.ndarray, List[float]]) -> List[float]:
    """
    Convert a quaternion into euler angles (roll, pitch, yaw).

    Args:
        quaternion (`np.ndarray` or `list`):
            The quaternion to convert.

    Returns:
        euler (`list`):
            The euler angles in radians (counterclockwise).
    """
    x, y, z, w = quaternion

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = np.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = np.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = np.arctan2(t3, t4)

    return [roll_x, pitch_y, yaw_z]  # in radians
