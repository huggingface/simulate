# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import warnings
from typing import Any, List, Optional, Sequence, Type, Union

import numpy as np

from ...utils import logging
from .space import Space


logger = logging.get_logger(__name__)


class Box(Space):
    """
    A (possibly unbounded) box in R^n. Specifically, a Box represents the
    Cartesian product of n closed intervals. Each interval has the form of one
    of [a, b], (-oo, b], [a, oo), or (-oo, oo).

    Args:
        low (`int` or `float` or `np.ndarray`):
            Lower bound of the box. If a float, the bound is shared by all dimensions.
            If an array, each dimension can have its own bound.
        high (`int` or `float` or `np.ndarray`):
            Upper bound of the box. If a float, the bound is shared by all dimensions.
            If an array, each dimension can have its own bound.
        shape (`Sequence[int]`, *optional*, default `None`):
            Shape of the box. If `None`, the shape is inferred from the shape of `low` or `high`.
        dtype (`np.dtype`, *optional*, default `np.float32`):
            Data type of the box.
        seed (`int`, *optional*, default `None`):
            Seed for the random number generator.


    Examples:
    ```python
    # Identical bound for each dimension:
    Box(low=-1.0, high=2.0, shape=(3, 4), dtype=np.float32) # Box(3, 4)

    # Independent bound for each dimension:
    Box(low=np.array([-1.0, -2.0]), high=np.array([2.0, 4.0]), dtype=np.float32) # Box(2,)
    ```
    """

    def __init__(
        self,
        low: Union[np.ndarray, float, int],
        high: Union[np.ndarray, float, int],
        shape: Optional[Sequence[int]] = None,
        dtype: Union[Type, str, object] = np.float32,
        seed: Optional[int] = None,
    ):
        assert dtype is not None, "dtype must be explicitly provided. "
        self.dtype = np.dtype(dtype)

        # determine shape if it isn't provided directly
        if shape is not None:
            shape = tuple(shape)
            assert np.isscalar(low) or low.shape == shape, "low.shape doesn't match provided shape"
            assert np.isscalar(high) or high.shape == shape, "high.shape doesn't match provided shape"
        elif not np.isscalar(low):
            shape = low.shape
            assert np.isscalar(high) or high.shape == shape, "high.shape doesn't match low.shape"
        elif not np.isscalar(high):
            shape = high.shape
            assert np.isscalar(low) or low.shape == shape, "low.shape doesn't match high.shape"
        else:
            raise ValueError("shape must be provided or inferred from the shapes of low or high")

        if np.isscalar(low):
            low = np.full(shape, low, dtype=dtype)

        if np.isscalar(high):
            high = np.full(shape, high, dtype=dtype)

        self._shape = shape
        self.low = low
        self.high = high

        def _get_precision(np_dtype: Union[Type, str, dtype]) -> int:
            """
            Get the precision of a numpy dtype.

            Args:
                np_dtype (`np.dtype` or `str` or `type`):
                    Numpy dtype.

            Returns:
                precision (`int`):
                    Precision of the numpy dtype.
            """
            if np.issubdtype(np_dtype, np.floating):
                return np.finfo(np_dtype).precision
            else:
                return np.inf

        low_precision = _get_precision(self.low.dtype)
        high_precision = _get_precision(self.high.dtype)
        dtype_precision = _get_precision(self.dtype)
        if min(low_precision, high_precision) > dtype_precision:
            logger.warning(f"Box bound precision lowered by casting to {self.dtype}")
        self.low = self.low.astype(self.dtype)
        self.high = self.high.astype(self.dtype)

        # Boolean arrays which indicate the interval type for each coordinate
        self.bounded_below = -np.inf < self.low
        self.bounded_above = np.inf > self.high

        super(Box, self).__init__(self.shape, self.dtype, seed)

    def is_bounded(self, manner: str = "both") -> bool:
        """
        Check if the box is bounded.

        Args:
            manner (`str`, *optional*, default `both`):
                Manner in which the box is bounded. Can be either `both`, `below`, or `above`.

        Returns:
            bounded (`bool`):
                Whether the box is bounded.
        """
        below = np.all(self.bounded_below)
        above = np.all(self.bounded_above)
        if manner == "both":
            return below and above
        elif manner == "below":
            return below
        elif manner == "above":
            return above
        else:
            raise ValueError("manner is not in {'below', 'above', 'both'}")

    def sample(self) -> np.ndarray:
        """
        Generates a single random sample inside the Box.

        In creating a sample of the box, each coordinate is sampled according to
        the form of the interval:

        * [a, b] : uniform distribution
        * [a, oo) : shifted exponential distribution
        * (-oo, b] : shifted negative exponential distribution
        * (-oo, oo) : normal distribution

        Returns:
            sample (`np.ndarray`):
                Random sample inside the box.
        """
        high = self.high if self.dtype.kind == "f" else self.high.astype("int64") + 1
        sample = np.empty(self.shape)

        # Masking arrays which classify the coordinates according to interval
        # type
        unbounded = ~self.bounded_below & ~self.bounded_above
        upp_bounded = ~self.bounded_below & self.bounded_above
        low_bounded = self.bounded_below & ~self.bounded_above
        bounded = self.bounded_below & self.bounded_above

        # Vectorized sampling by interval type
        sample[unbounded] = self.np_random.normal(size=unbounded[unbounded].shape)

        sample[low_bounded] = self.np_random.exponential(size=low_bounded[low_bounded].shape) + self.low[low_bounded]

        sample[upp_bounded] = -self.np_random.exponential(size=upp_bounded[upp_bounded].shape) + self.high[upp_bounded]

        sample[bounded] = self.np_random.uniform(
            low=self.low[bounded], high=high[bounded], size=bounded[bounded].shape
        )
        if self.dtype.kind == "i":
            sample = np.floor(sample)

        return sample.astype(self.dtype)

    def contains(self, x: Any) -> bool:
        """
        Check if a sample is inside the box.

        Args:
            x (`np.ndarray`):
                Sample to check.

        Returns:
            inside (`bool`):
                Whether the sample is inside the box.
        """
        if not isinstance(x, np.ndarray):
            warnings.warn("Casting input x to numpy array.")
            x = np.asarray(x, dtype=self.dtype)

        return (
            np.can_cast(x.dtype, self.dtype)
            and x.shape == self.shape
            and np.all(x >= self.low)
            and np.all(x <= self.high)
        )

    def to_jsonable(self, sample_n: List[Any]):
        """
        Convert a batch of samples to a JSONable data type (e.g. `list`).

        Args:
            sample_n (`List[Any]`):
                Batch of samples to convert.

        Returns:
            jsonable_sample_n (`List[Any]`):
                JSONable batch of samples.
        """
        return np.array(sample_n).tolist()

    def from_jsonable(self, sample_n: List[Any]) -> List[Any]:
        """
        Convert a batch of JSONable samples to a tensor.

        Args:
            sample_n (`List[Any]`):
                Batch of JSONable samples to convert.

        Returns:
            sample_n (`List[Any]`):
                Batch of samples.
        """
        return [np.asarray(sample) for sample in sample_n]

    def __repr__(self) -> str:
        return f"Box({self.low}, {self.high}, {self.shape}, {self.dtype})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Box)
            and (self.shape == other.shape)
            and np.allclose(self.low, other.low)
            and np.allclose(self.high, other.high)
        )
