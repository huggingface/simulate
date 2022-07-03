from enum import Enum


class RigidbodyConstraints(str, Enum):
    FREEZE_POSITION_X = "freeze_position_x"
    FREEZE_POSITION_Y = "freeze_position_y"
    FREEZE_POSITION_Z = "freeze_position_z"
    FREEZE_ROTATION_X = "freeze_rotation_x"
    FREEZE_ROTATION_Y = "freeze_rotation_y"
    FREEZE_ROTATION_Z = "freeze_rotation_z"
