# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import Any, List, Optional, Tuple, Type, Union

import numpy as np

from ...utils import logging
from .discrete import Discrete
from .space import Space


logger = logging.get_logger(__name__)


class MultiDiscrete(Space):
    """
    - The multi-discrete action space consists of a series of discrete action spaces
        with different number of actions in each
    - It is useful to represent game controllers or keyboards
        where each key can be represented as a discrete action space
    - It is parametrized by passing an array of positive integers specifying number of actions
        for each discrete action space

    Note: Some environment wrappers assume a value of 0 always represents the NOOP action.

    e.g. Nintendo Game Controller
    - Can be conceptualized as 3 discrete action spaces:

        1) Arrow Keys: Discrete 5  - NOOP[0], UP[1], RIGHT[2], DOWN[3], LEFT[4]  - params: min: 0, max: 4
        2) Button A:   Discrete 2  - NOOP[0], Pressed[1] - params: min: 0, max: 1
        3) Button B:   Discrete 2  - NOOP[0], Pressed[1] - params: min: 0, max: 1

    - Can be initialized as

        MultiDiscrete([ 5, 2, 2 ])

    """

    def __init__(self, nvec: List[int], dtype: Union[Type, str] = np.int64, seed: Optional[int] = None):
        """
        nvec: vector of counts of each categorical variable
        """
        assert (np.array(nvec) > 0).all(), "nvec (counts) have to be positive"
        self.nvec = np.asarray(nvec, dtype=dtype)

        super(MultiDiscrete, self).__init__(self.nvec.shape, dtype, seed)

    def sample(self) -> Tuple[Any, ...]:
        return (self.np_random.random_sample(self.nvec.shape) * self.nvec).astype(self.dtype)

    def contains(self, x: Any) -> bool:
        if isinstance(x, list):
            x = np.array(x)  # Promote list to array for contains check
        # if nvec is uint32 and space dtype is uint32, then 0 <= x < self.nvec guarantees that x
        # is within correct bounds for space dtype (even though x does not have to be unsigned)
        return x.shape == self.shape and (0 <= x).all() and (x < self.nvec).all()

    def to_jsonable(self, sample_n: np.ndarray) -> List[Any]:
        return [sample.tolist() for sample in sample_n]

    def from_jsonable(self, sample_n: List[Any]) -> np.ndarray:
        return np.array(sample_n)

    def __repr__(self) -> str:
        return "MultiDiscrete({})".format(self.nvec)

    def __getitem__(self, index: int) -> Union[Discrete, "MultiDiscrete"]:
        nvec = self.nvec[index]
        if nvec.ndim == 0:
            subspace = Discrete(nvec)
        else:
            subspace = MultiDiscrete(nvec, self.dtype)
        subspace.np_random.set_state(self.np_random.get_state())  # for reproducibility
        return subspace

    def __len__(self) -> int:
        if self.nvec.ndim >= 2:
            logger.warning("Get length of a multi-dimensional MultiDiscrete space.")
        return len(self.nvec)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MultiDiscrete) and np.all(self.nvec == other.nvec)
