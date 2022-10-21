# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import typing
from collections import OrderedDict
from typing import Any, List, Optional, Sequence, Tuple, Union

import numpy as np

from ...utils import logging
from .space import Space


logger = logging.get_logger(__name__)


class Dict(Space):
    """
    A dictionary of simpler spaces.

    Args:
        spaces (`Dict[str, Space]` or `Sequence[Tuple[str, Space]]`, *optional*, defaults to `None`):
            A dictionary of simpler spaces, or a list of (key, space) pairs.
        seed (`int`, *optional*, defaults to `None`):
            The seed to use to seed the RNG of this space.

    Examples:
    ```python
    # Simple
    self.observation_space = spaces.Dict({"position": spaces.Discrete(2), "velocity": spaces.Discrete(3)})

    # Nested
    self.nested_observation_space = spaces.Dict({
        'sensors':  spaces.Dict({
            'position': spaces.Box(low=-100, high=100, shape=(3,)),
            'velocity': spaces.Box(low=-1, high=1, shape=(3,)),
            'front_cam': spaces.Tuple((
                spaces.Box(low=0, high=1, shape=(10, 10, 3)),
                spaces.Box(low=0, high=1, shape=(10, 10, 3))
            )),
            'rear_cam': spaces.Box(low=0, high=1, shape=(10, 10, 3)),
        }),
        'ext_controller': spaces.MultiDiscrete((5, 2, 2)),
        'inner_state':spaces.Dict({
            'charge': spaces.Discrete(100),
            'system_checks': spaces.MultiBinary(10),
            'job_status': spaces.Dict({
                'task': spaces.Discrete(5),
                'progress': spaces.Box(low=0, high=100, shape=()),
            })
        })
    })
    ```
    """

    def __init__(
        self,
        spaces: Optional[
            Union[
                typing.Dict[str, Space],
                Sequence[Tuple[str, Space]],
            ]
        ] = None,
        seed: Optional[int] = None,
        **spaces_kwargs: Any,
    ):
        assert (spaces is None) or (not spaces_kwargs), "Use either Dict(spaces=dict(...)) or Dict(foo=x, bar=z)"

        if spaces is None:
            spaces = spaces_kwargs
        if isinstance(spaces, dict) and not isinstance(spaces, OrderedDict):
            spaces = OrderedDict(sorted(list(spaces.items())))
        if isinstance(spaces, list):
            spaces = OrderedDict(spaces)
        self.spaces = spaces
        for space in spaces.values():
            assert isinstance(space, Space), "Values of the dict should be instances of gym.Space"
        super(Dict, self).__init__(None, None, seed)  # None for shape and dtype, since it'll require special handling

    def seed(self, seed: Optional[Union[int, dict]] = None) -> list:
        """
        Seed the RNG of these spaces.

        Args:
            seed (`int` or `dict`, *optional*, defaults to `None`):
                The seed to use to seed the RNG of these spaces.

        Returns:
            seeds (`list`):
                The list of seeds used to seed the RNG of these spaces.
        """
        seeds = []
        if isinstance(seed, dict):
            for key, seed_key in zip(self.spaces, seed):
                assert key == seed_key, logger.error(
                    f"Key value {seed_key} in passed seed dict did not match key value {key} in spaces Dict.",
                )
                seeds += self.spaces[key].seed(seed[seed_key])
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

            for subspace, subseed in zip(self.spaces.values(), subseeds):
                seeds.append(subspace.seed(int(subseed))[0])
        elif seed is None:
            for space in self.spaces.values():
                seeds += space.seed(seed)
        else:
            raise TypeError("Passed seed not of an expected type: dict or int or None")

        return seeds

    def sample(self) -> OrderedDict:
        """
        Sample a random element for each space in the dict.

        Returns:
            samples (`OrderedDict`):
                The sampled elements.
        """
        return OrderedDict([(k, space.sample()) for k, space in self.spaces.items()])

    def contains(self, x: Any) -> bool:
        """
        Check if the given element is contained in one of the spaces.

        Args:
            x (`Any`):
                The element to check.

        Returns:
            contained (`bool`):
                Whether the element is contained in one of the spaces.
        """
        if not isinstance(x, dict) or len(x) != len(self.spaces):
            return False
        for k, space in self.spaces.items():
            if k not in x:
                return False
            if not space.contains(x[k]):
                return False
        return True

    def __getitem__(self, key: Union[int, str]) -> Space:
        return self.spaces[key]

    def __setitem__(self, key: Union[int, str], value: Space):
        self.spaces[key] = value

    def __iter__(self):
        for key in self.spaces:
            yield key

    def __len__(self) -> int:
        return len(self.spaces)

    def __contains__(self, item: Any) -> bool:
        return self.contains(item)

    def __repr__(self) -> str:
        return "Dict(" + ", ".join([str(k) + ":" + str(s) for k, s in self.spaces.items()]) + ")"

    def to_jsonable(self, sample_n: List[Any]) -> dict:
        """
        Serialize as dict-repr of vectors.

        Args:
            sample_n (`List[Any]`):
                The samples to serialize.

        Returns:
            jsonable (`dict`):
                The serialized samples.
        """
        return {key: space.to_jsonable([sample[key] for sample in sample_n]) for key, space in self.spaces.items()}

    def from_jsonable(self, sample_n: dict) -> List[Any]:
        """
        Deserialize as list of dicts.

        Args:
            sample_n (`dict`):
                The samples to deserialize.

        Returns:
            samples (`List[Any]`):
                The deserialized samples.
        """
        dict_of_list = {}
        key = None
        for key, space in self.spaces.items():
            dict_of_list[key] = space.from_jsonable(sample_n[key])
        ret = []
        for i, _ in enumerate(dict_of_list[key]):
            entry = {}
            for key, value in dict_of_list.items():
                entry[key] = value[i]
            ret.append(entry)
        return ret

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Dict) and self.spaces == other.spaces

    def keys(self):
        return self.spaces.keys()

    def values(self):
        return self.spaces.values()

    def items(self):
        return self.spaces.items()
