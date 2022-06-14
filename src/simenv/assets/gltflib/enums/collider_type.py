from enum import Enum


class ColliderType(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    MESH = "MESH"
