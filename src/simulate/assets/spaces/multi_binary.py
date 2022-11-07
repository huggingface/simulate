# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import Any, List, Optional, Union

import numpy as np

from .space import Space


class MultiBinary(Space):
    """
    An n-shape binary space.

    Args:
        n (`int` or `list`):
            The shape of the space.

    Examples:
    ```python
    self.observation_space = spaces.MultiBinary(5)
    self.observation_space.sample()
    # array([0,1,0,1,0], dtype=int8)

    self.observation_space = spaces.MultiBinary([3,2])
    self.observation_space.sample()
    # array([[0, 0], [0, 1], [1, 1]], dtype=int8)
    ```
    """

    def __init__(self, n: int, seed: Optional[int] = None):
        self.n = n
        if type(n) in [tuple, list, np.ndarray]:
            input_n = n
        else:
            input_n = (n,)
        super(MultiBinary, self).__init__(input_n, np.int8, seed)

    def sample(self) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Sample a random element of this space.

        Returns:
            sample (`np.ndarray` or `List[np.ndarray]`):
                A random element of this space.
        """
        return self.np_random.randint(low=0, high=2, size=self.n, dtype=self.dtype)

    def contains(self, x: Any) -> bool:
        """
        Check if `x` is a valid element of this space.

        Args:
            x (`Any`):
                The element to check.

        Returns:
            valid (`bool`):
                Whether `x` is a valid element of this space.
        """
        if isinstance(x, list) or isinstance(x, tuple):
            x = np.array(x)  # Promote list to array for contains check
        if self.shape != x.shape:
            return False
        return ((x == 0) | (x == 1)).all()

    def to_jsonable(self, sample_n: List[Any]):
        """
        Convert a sample from this space to a JSONable type.

        Args:
            sample_n (`List[Any]`):
                The sample to convert.

        Returns:
            jsonable (`List[Any]`):
                The converted sample.
        """
        return np.array(sample_n).tolist()

    def from_jsonable(self, sample_n: List[Any]) -> List[Any]:
        """
        Convert a sample from a JSONable type to this space.

        Args:
            sample_n (`List[Any]`):
                The sample to convert.

        Returns:
            sample (`List[Any]`):
                The converted sample.
        """
        return [np.asarray(sample) for sample in sample_n]

    def __repr__(self) -> str:
        return "MultiBinary({})".format(self.n)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MultiBinary) and self.n == other.n
