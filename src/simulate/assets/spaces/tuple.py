# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import typing
from typing import Any, List, Optional, Union

import numpy as np

from .space import Space


class Tuple(Space):
    """
    A tuple (i.e., product) of simpler spaces

    Args:
        spaces (`Tuple[Space, ...]`):
            Spaces which are members of the tuple.
        seed (`int`, *optional*, defaults to `None`):
            Seed for the random number generator.

    Examples:
    ```python
    self.observation_space = spaces.Tuple((spaces.Discrete(2), spaces.Discrete(3)))
    ```
    """

    def __init__(self, spaces: typing.Tuple[Space, ...], seed: Optional[int] = None):
        self.spaces = spaces
        for space in spaces:
            assert isinstance(space, Space), "Elements of the tuple must be instances of gym.Space"
        super(Tuple, self).__init__(None, None, seed)

    def seed(self, seed: Optional[int] = None) -> List[int]:
        """
        Seed the underlying random number generator.

        Args:
            seed (`int`, *optional*, defaults to `None`):
                Seed for the random number generator.

        Returns:
            seeds (`List[int]`):
                List of seeds used in the spaces' random number generators.
        """
        seeds = []

        if isinstance(seed, list):
            for i, space in enumerate(self.spaces):
                seeds += space.seed(seed[i])
        elif isinstance(seed, int):
            seeds = super().seed(seed)
            try:
                subseeds = self.np_random.choice(
                    np.iinfo(int).max,
                    size=len(self.spaces),
                    replace=False,  # unique subseed for each subspace
                )
            except ValueError:
                subseeds = self.np_random.choice(
                    np.iinfo(int).max,
                    size=len(self.spaces),
                    replace=True,  # we get more than INT_MAX subspaces
                )

            for subspace, subseed in zip(self.spaces, subseeds):
                seeds.append(subspace.seed(int(subseed))[0])
        elif seed is None:
            for space in self.spaces:
                seeds += space.seed(seed)
        else:
            raise TypeError("Passed seed not of an expected type: list or int or None")

        return seeds

    def sample(self) -> typing.Tuple[Any, ...]:
        """
        Sample a random element of this space.

        Returns:
            sample (`Tuple[Any, ...]`):
                Sampled elements from the spaces.
        """
        return tuple([space.sample() for space in self.spaces])

    def contains(self, x: Any) -> bool:
        """
        Check if the space contains the element `x`.

        Args:
            x (`Any`):
                Element to check.

        Returns:
            contains (`bool`):
                Whether the space contains the element `x`.
        """
        if isinstance(x, list):
            x = tuple(x)  # Promote list to tuple for contains check
        return (
            isinstance(x, tuple)
            and len(x) == len(self.spaces)
            and all(space.contains(part) for (space, part) in zip(self.spaces, x))
        )

    def __repr__(self) -> str:
        return "Tuple(" + ", ".join([str(s) for s in self.spaces]) + ")"

    def to_jsonable(self, sample_n: List[Any]) -> List[Any]:
        """
        Convert a batch of samples from this space to a JSONable representation.

        Args:
            sample_n (`List[Any]`):
                Batch of samples from this space.

        Returns:
            jsonable (`List[Any]`):
                JSONable representation of the batch of samples.
        """
        # serialize as list-repr of tuple of vectors
        return [space.to_jsonable([sample[i] for sample in sample_n]) for i, space in enumerate(self.spaces)]

    def from_jsonable(self, sample_n: List[Any]) -> List[Any]:
        """
        Convert a batch of JSONable samples to space samples.

        Args:
            sample_n (`List[Any]`):
                Batch of samples from these spaces.
        """
        return [sample for sample in zip(*[space.from_jsonable(sample_n[i]) for i, space in enumerate(self.spaces)])]

    def __getitem__(self, index: Union[int, slice]) -> Union[Space, typing.Tuple[Space, ...]]:
        return self.spaces[index]

    def __len__(self) -> int:
        return len(self.spaces)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Tuple) and self.spaces == other.spaces
