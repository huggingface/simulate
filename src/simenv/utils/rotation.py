import math

import numpy as np


def quat_from_euler(x, y, z):
    qx = np.sin(x / 2) * np.cos(y / 2) * np.cos(z / 2) - np.cos(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    qy = np.cos(x / 2) * np.sin(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.cos(y / 2) * np.sin(z / 2)
    qz = np.cos(x / 2) * np.cos(y / 2) * np.sin(z / 2) - np.sin(x / 2) * np.sin(y / 2) * np.cos(z / 2)
    qw = np.cos(x / 2) * np.cos(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    return [qx, qy, qz, qw]


def quat_from_degrees(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))
