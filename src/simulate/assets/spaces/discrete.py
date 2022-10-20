# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import Any, Optional

import numpy as np

from .space import Space


class Discrete(Space):
    r"""
    A discrete space in :math:`\{ 0, 1, \\dots, n-1 \}`.

    Args:
        n (`int`):
            Dimension of the discrete space.
        seed (`int`, `optional`, defaults to `None`):
            Seed for the underlying random number generator.

    Examples:
    ```python
    Discrete(2)
    ```

    """

    def __init__(self, n: int, seed: Optional[int] = None):
        assert n >= 0
        self.n = n
        super(Discrete, self).__init__((), np.int64, seed)

    def sample(self) -> int:
        """
        Sample a random element of this space.

        Returns:
            sample (`int`):
                A random element of this space.
        """
        return self.np_random.randint(self.n)

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
        if isinstance(x, int):
            as_int = x
        elif isinstance(x, (np.generic, np.ndarray)) and (
            x.dtype.char in np.typecodes["AllInteger"] and x.shape == ()
        ):
            as_int = int(x)
        else:
            return False
        return 0 <= as_int < self.n

    def __repr__(self) -> str:
        return "Discrete(%d)" % self.n

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Discrete) and self.n == other.n
