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
from typing import TYPE_CHECKING, Callable, Iterator, Tuple

from .abstractiter import AbstractIter


if TYPE_CHECKING:
    from ..asset import Asset


class PreOrderIter(AbstractIter):
    """
    Iterate over tree applying pre-order strategy starting at `node`.

    Start at root and go-down until reaching a leaf node.
    Step upwards then, and search for the next leafs.

    >>> from anytree import Node, RenderTree, AsciiStyle, PreOrderIter
    >>> f = Node("f")
    >>> b = Node("b", parent=f)
    >>> a = Node("a", parent=b)
    >>> d = Node("d", parent=b)
    >>> c = Node("c", parent=d)
    >>> e = Node("e", parent=d)
    >>> g = Node("g", parent=f)
    >>> i = Node("i", parent=g)
    >>> h = Node("h", parent=i)
    >>> print(RenderTree(f, style=AsciiStyle()).by_attr())
    f
    |-- b
    |   |-- a
    |   +-- d
    |       |-- c
    |       +-- e
    +-- g
        +-- i
            +-- h
    >>> [node.name for node in PreOrderIter(f)]
    ['f', 'b', 'a', 'd', 'c', 'e', 'g', 'i', 'h']
    >>> [node.name for node in PreOrderIter(f, maxlevel=3)]
    ['f', 'b', 'a', 'd', 'g', 'i']
    >>> [node.name for node in PreOrderIter(f, filter_=lambda n: n.name not in ('e', 'g'))]
    ['f', 'b', 'a', 'd', 'c', 'i', 'h']
    >>> [node.name for node in PreOrderIter(f, stop=lambda n: n.name == 'd')]
    ['f', 'b', 'a', 'g', 'i', 'h']
    """

    @staticmethod
    def _iter(
        children: Tuple["Asset", ...], filter_: Callable[["Asset"], bool], stop, maxlevel: int
    ) -> Iterator["Asset"]:
        for child_ in children:
            if stop(child_):
                continue
            if filter_(child_):
                yield child_
            if not AbstractIter._abort_at_level(2, maxlevel):
                descendantmaxlevel = maxlevel - 1 if maxlevel else None
                for descendant_ in PreOrderIter._iter(child_.tree_children, filter_, stop, descendantmaxlevel):
                    yield descendant_
