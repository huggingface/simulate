from enum import Enum


class AccessorType(
    str, Enum
):  # This is an equivalent StrEnum class (see https://docs.python.org/3/library/enum.html#others0)
    SCALAR = "SCALAR"
    VEC2 = "VEC2"
    VEC3 = "VEC3"
    VEC4 = "VEC4"
    MAT2 = "MAT2"
    MAT3 = "MAT3"
    MAT4 = "MAT4"
