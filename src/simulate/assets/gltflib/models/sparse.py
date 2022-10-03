from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel
from .sparse_indices import SparseIndices
from .sparse_values import SparseValues


@dataclass_json
@dataclass
class Sparse(BaseModel):
    """
    Sparse storage of attributes that deviate from their initialization value.

    Properties:
    count (integer) Number of entries stored in the sparse array. (Required)
    indices (object) Index array of size count that points to those accessor attributes that deviate from their
        initialization value. Indices must strictly increase. (Required)
    values (object) Array of size count times number of components, storing the displaced accessor attributes pointed by
        indices. Substituted values must have the same componentType and number of components as the base accessor.
        (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    count: Optional[int] = None
    indices: Optional[SparseIndices] = None
    values: Optional[SparseValues] = None
