# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import operator as op
import typing
from collections import OrderedDict
from functools import reduce, singledispatch
from typing import Union

import numpy as np

from . import Box, Dict, Discrete, MultiBinary, MultiDiscrete, Space, Tuple


@singledispatch
def flatdim(space: Space) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `Space` would have.

    Args:
        space (`Space`):
            The `Space` to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `Space` would have.
    """
    raise NotImplementedError(f"Unknown space: `{space}`")


@flatdim.register(Box)
@flatdim.register(MultiBinary)
def flatdim_box_multibinary(space: Union[Box, MultiBinary]) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `Box` or `MultiBinary` space would have.

    Args:
        space (`Box` or `MultiBinary`):
            The `Box` or `MultiBinary` space to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `Box` or `MultiBinary` space would have.
    """
    return reduce(op.mul, space.shape, 1)


@flatdim.register(Discrete)
def flatdim_discrete(space: Discrete) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `Discrete` space would have.

    Args:
        space (`Discrete`):
            The `Discrete` space to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `Discrete` space would have.
    """
    return int(space.n)


@flatdim.register(MultiDiscrete)
def flatdim_multidiscrete(space: MultiDiscrete) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `MultiDiscrete` space would have.

    Args:
        space (`MultiDiscrete`):
            The `MultiDiscrete` space to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `MultiDiscrete` space would have.
    """
    return int(np.sum(space.nvec))


@flatdim.register(Tuple)
def flatdim_tuple(space: Tuple) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `Tuple` of spaces would have.

    Args:
        space (`Tuple`):
            The `Tuple` of spaces to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `Tuple` of spaces would have.
    """
    return sum([flatdim(s) for s in space.spaces])


@flatdim.register(Dict)
def flatdim_dict(space: Dict) -> int:
    """
    Get the number of dimensions a flattened equivalent of this `Dict` of spaces would have.

    Args:
        space (`Dict`):
            The `Dict` of spaces to get the number of dimensions of.

    Returns:
        dim (`int`):
            The number of dimensions a flattened equivalent of this `Dict` of spaces would have.
    """
    return sum([flatdim(s) for s in space.spaces.values()])


@singledispatch
def flatten(space: Space, x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `Space`.

    This is useful when e.g. points from spaces must be passed to a neural
    network, which only understands flat arrays of floats.

    Args:
        space (`Space`):
            The `Space` to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point.
    """
    raise NotImplementedError(f"Unknown space: `{space}`")


@flatten.register(Box)
@flatten.register(MultiBinary)
def flatten_box_multibinary(space: Union[Box, MultiBinary], x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `Box` or `MultiBinary` space.

    Args:
        space (`Box` or `MultiBinary`):
            The `Box` or `MultiBinary` space to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point.
    """
    return np.asarray(x, dtype=space.dtype).flatten()


@flatten.register(Discrete)
def flatten_discrete(space: Discrete, x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `Discrete` space.

    Args:
        space (`Discrete`):
            The `Discrete` space to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point (one hot tensor).
    """
    onehot = np.zeros(space.n, dtype=space.dtype)
    onehot[x] = 1
    return onehot


@flatten.register(MultiDiscrete)
def flatten_multidiscrete(space: MultiDiscrete, x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `MultiDiscrete` space.

    Args:
        space (`MultiDiscrete`):
            The `MultiDiscrete` space to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point (one hot tensor).
    """
    offsets = np.zeros((space.nvec.size + 1,), dtype=space.dtype)
    offsets[1:] = np.cumsum(space.nvec.flatten())

    onehot = np.zeros((offsets[-1],), dtype=space.dtype)
    onehot[offsets[:-1] + x.flatten()] = 1
    return onehot


@flatten.register(Tuple)
def flatten_tuple(space: Tuple, x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `Tuple` of spaces.

    Args:
        space (`Tuple`):
            The `Tuple` of spaces to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point.
    """
    return np.concatenate([flatten(s, x_part) for x_part, s in zip(x, space.spaces)])


@flatten.register(Dict)
def flatten_dict(space: Dict, x: np.ndarray) -> np.ndarray:
    """
    Flatten a data point from a `Dict` of spaces.

    Args:
        space (`Dict`):
            The `Dict` of spaces to flatten the data point from.
        x (`np.ndarray`):
            The data point to flatten.

    Returns:
        x_flat (`np.ndarray`):
            The flattened data point.
    """
    return np.concatenate([flatten(s, x[key]) for key, s in space.spaces.items()])


@singledispatch
def unflatten(space: Space, x: np.ndarray) -> np.ndarray:
    """
    Unflatten a data point from a `Space`. This reverses the transformation applied by `flatten()`.

    Args:
        space (`Space`):
            The `Space` to unflatten the data point from.
            Ensure that this is the same space as for the `flatten()` call.
        x (`np.ndarray`):
            The data point to unflatten.

    Returns:
        x_unflat (`np.ndarray`):
            The un-flattened data point, matching the space structure.
    """
    raise NotImplementedError(f"Unknown space: `{space}`")


@unflatten.register(Box)
@unflatten.register(MultiBinary)
def unflatten_box_multibinary(space: Union[Box, MultiBinary], x: np.ndarray) -> np.ndarray:
    """
    Unflatten a data point from a Box or MultiBinary space.

    Args:
        space (`Box` or `MultiBinary`):
            The `Box` or `MultiBinary` space to unflatten the data point from.
            Ensure that this is the same space as for the `flatten()` call.
        x (`np.ndarray`):
            The data point to unflatten.

    Returns:
        x_unflat (`np.ndarray`):
            The un-flattened data point, matching the space structure.
    """
    return np.asarray(x, dtype=space.dtype).reshape(space.shape)


@unflatten.register(Discrete)
def unflatten_discrete(space: Discrete, x: np.ndarray) -> int:
    """
    Unflatten a data point from a `Discrete` space.

    Args:
        space (`Discrete`):
            The `Discrete` space to unflatten the data point from.
            Ensure that this is the same space as for the `flatten()` call.
        x (`np.ndarray`):
            The data point to unflatten.

    Returns:
        x_unflat (`int`):
            The un-flattened data point, matching the space structure.
    """
    return int(np.nonzero(x)[0][0])


@unflatten.register(MultiDiscrete)
def unflatten_multidiscrete(space: MultiDiscrete, x: np.ndarray) -> np.ndarray:
    """
    Unflatten a data point from a MultiDiscrete space.

    Args:
        space (`MultiDiscrete`):
            The `MultiDiscrete` space to unflatten the data point from.
            Ensure that this is the same `space` as for the `flatten()` call.
        x (`np.ndarray`):
            The data point to unflatten.

    Returns:
        x_unflat (`np.ndarray`):
            The un-flattened data point, matching the space structure.
    """
    offsets = np.zeros((space.nvec.size + 1,), dtype=space.dtype)
    offsets[1:] = np.cumsum(space.nvec.flatten())

    (indices,) = np.nonzero(x)
    return np.asarray(indices - offsets[:-1], dtype=space.dtype).reshape(space.shape)


@unflatten.register(Tuple)
def unflatten_tuple(space: Tuple, x: np.ndarray) -> typing.Tuple[np.ndarray, ...]:
    """
    Unflatten data points from a `Tuple` of spaces.

    Args:
        space (`Tuple`):
            The `Tuple` of spaces to unflatten the data points from.
            Ensure that this is the same spaces as for the `flatten()` call.
        x (`np.ndarray`):
            The data points to unflatten.

    Returns:
        x_unflat (`Tuple[np.ndarray, ...]`):
            The un-flattened data points, matching the spaces structure.
    """
    dims = np.asarray([flatdim(s) for s in space.spaces], dtype=np.int_)
    list_flattened = np.split(x, np.cumsum(dims[:-1]))
    return tuple(unflatten(s, flattened) for flattened, s in zip(list_flattened, space.spaces))


@unflatten.register(Dict)
def unflatten_dict(space: Dict, x: np.ndarray) -> OrderedDict:
    """
    Unflatten data points from a `Dict` of spaces.

    Args:
        space (`Dict`):
            The `Dict` of spaces to unflatten the data points from.
            Ensure that this is the same spaces as for the `flatten()` call.
        x (`np.ndarray`):
            The data points to unflatten.

    Returns:
        x_unflat (`OrderedDict`):
            The un-flattened data points, matching the spaces structure.
    """
    dims = np.asarray([flatdim(s) for s in space.spaces.values()], dtype=np.int_)
    list_flattened = np.split(x, np.cumsum(dims[:-1]))
    return OrderedDict(
        [(key, unflatten(s, flattened)) for flattened, (key, s) in zip(list_flattened, space.spaces.items())]
    )


@singledispatch
def flatten_space(space: Space) -> Box:
    """
    Flatten a `Space` into a single `Box`.

    This is equivalent to `flatten()`, but operates on the space itself. The
    result always is a `Box` with flat boundaries. The box has exactly
    `flatdim(space)` dimensions. Flattening a sample of the original space
    has the same effect as taking a sample of the flattened space.

    Args:
        space (`Space`):
            The `Space` to flatten.

    Returns:
        space_flat (`Box`):
            The space flattened into a `Box`.

    Examples:
    ```python
    box = Box(0.0, 1.0, shape=(3, 4, 5))
    box
    # Box(3, 4, 5)
    flatten_space(box)
    # Box(60,)
    flatten(box, box.sample()) in flatten_space(box)
    # True

    # Flatten a discrete space:
    discrete = Discrete(5)
    flatten_space(discrete)
    # Box(5,)
    flatten(box, box.sample()) in flatten_space(box)
    # True

    # Recursively flatten a dict:
    space = Dict({"position": Discrete(2),
                  "velocity": Box(0, 1, shape=(2, 2))})
    flatten_space(space)
    # Box(6,)
    flatten(space, space.sample()) in flatten_space(space)
    # True
    ```
    """
    raise NotImplementedError(f"Unknown space: `{space}`")


@flatten_space.register(Box)
def flatten_space_box(space: Box) -> Box:
    """
    Flatten a Box space into a single `Box`.

    Args:
        space (`Box`):
            The Box space to flatten.

    Returns:
        space_flat (`Box`):
            The space flattened into a `Box`.
    """
    return Box(space.low.flatten(), space.high.flatten(), dtype=space.dtype)


@flatten_space.register(Discrete)
@flatten_space.register(MultiBinary)
@flatten_space.register(MultiDiscrete)
def flatten_space_binary(space: Union[Discrete, MultiBinary, MultiDiscrete]) -> Box:
    """
    Flatten a `Discrete`, `MultiBinary` or `MultiDiscrete` space into a single `Box`.

    Args:
        space (`Discrete` or `MultiBinary` or `MultiDiscrete`):
            The space to flatten.

    Returns:
        space_flat (`Box`):
            The space flattened into a `Box`.
    """
    return Box(low=0, high=1, shape=(flatdim(space),), dtype=space.dtype)


@flatten_space.register(Tuple)
def flatten_space_tuple(space: Tuple) -> Box:
    """
    Flatten a `Tuple` of spaces into a single `Box`.

    Args:
        space (`Tuple`):
            The `Tuple` of spaces to flatten.

    Returns:
        space_flat (`Box`):
            The `Tuple` of spaces flattened into a `Box`.
    """
    space = [flatten_space(s) for s in space.spaces]
    return Box(
        low=np.concatenate([s.low for s in space]),
        high=np.concatenate([s.high for s in space]),
        dtype=np.result_type(*[s.dtype for s in space]),
    )


@flatten_space.register(Dict)
def flatten_space_dict(space: Dict) -> Box:
    """
    Flatten a `Dict` of spaces into a single `Box`.

    Args:
        space (`Dict`):
            The `Dict` of spaces to flatten.

    Returns:
        space_flat (`Box`):
            The `Dict` of spaces flattened into a `Box`.
    """
    space = [flatten_space(s) for s in space.spaces.values()]
    return Box(
        low=np.concatenate([s.low for s in space]),
        high=np.concatenate([s.high for s in space]),
        dtype=np.result_type(*[s.dtype for s in space]),
    )
