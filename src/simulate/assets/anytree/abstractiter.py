# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
from typing import TYPE_CHECKING, Callable, List, Optional, Union


if TYPE_CHECKING:
    from .nodemixin import NodeMixin


class AbstractIter(object):
    def __init__(
        self,
        node: "NodeMixin",
        filter_: Optional[Union[Callable[["NodeMixin"], bool]]] = None,
        stop=None,
        maxlevel: Optional[int] = None,
    ):
        """
        Iterate over tree starting at `node`.

        Base class for all iterators.

        Keyword Args:
            filter_: function called with every `node` as argument, `node` is returned if `True`.
            stop: stop iteration at `node` if `stop` function returns `True` for `node`.
            maxlevel (int): maximum descending in the node hierarchy.
        """
        self.node = node
        self.filter_ = filter_
        self.stop = stop
        self.maxlevel = maxlevel
        self.__iter = None

    def __init(self):
        node = self.node
        maxlevel = self.maxlevel
        filter_ = self.filter_ or AbstractIter.__default_filter
        stop = self.stop or AbstractIter.__default_stop
        children = [] if AbstractIter._abort_at_level(1, maxlevel) else AbstractIter._get_children([node], stop)
        return self._iter(children, filter_, stop, maxlevel)

    @staticmethod
    def __default_filter(node: "NodeMixin") -> bool:
        return True

    @staticmethod
    def __default_stop(node: "NodeMixin") -> bool:
        return False

    def __iter__(self) -> "AbstractIter":
        return self

    def __next__(self):
        if self.__iter is None:
            self.__iter = self.__init()
        return next(self.__iter)

    @staticmethod
    def _iter(children: List["NodeMixin"], filter_: Callable[["NodeMixin"], bool], stop, maxlevel: int):
        raise NotImplementedError()  # pragma: no cover

    @staticmethod
    def _abort_at_level(level: int, maxlevel: int) -> bool:
        return maxlevel is not None and level > maxlevel

    @staticmethod
    def _get_children(children: List["NodeMixin"], stop) -> List["NodeMixin"]:
        return [child for child in children if not stop(child)]
