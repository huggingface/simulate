import math

import numpy as np

from .assets import quat_from_euler

def degrees_to_radians(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))
