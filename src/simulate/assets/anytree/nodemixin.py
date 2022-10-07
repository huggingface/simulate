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

# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Sequence, Tuple, Union

from .exceptions import LoopError, TreeError
from .preorderiter import PreOrderIter
from .render import RenderTree


if TYPE_CHECKING:
    from ..asset import Asset


class NodeMixin(object):

    tree_separator = "/"

    """
    The :any:`NodeMixin` class extends any Python class to a tree node.

    The only tree relevant information is the `parent` attribute.
    If `None` the :any:`NodeMixin` is root node.
    If set to another node, the :any:`NodeMixin` becomes the child of it.

    The `children` attribute can be used likewise.
    If `None` the :any:`NodeMixin` has no children.
    The `children` attribute can be set to any iterable of :any:`NodeMixin` instances.
    These instances become children of the node.

    >>> from anytree import NodeMixin, RenderTree
    >>> class MyBaseClass(object):  # Just an example of a base class
    ...     foo = 4
    >>> class MyClass(MyBaseClass, NodeMixin):  # Add Node feature
    ...     def __init__(self, name, length, width, parent=None, children=None):
    ...         super(MyClass, self).__init__()
    ...         self.name = name
    ...         self.tree_length = length
    ...         self.tree_width = width
    ...         self.tree_parent = parent
    ...         if children:
    ...             self.tree_children = children

    Construction via `parent`:

    >>> my0 = MyClass('my0', 0, 0)
    >>> my1 = MyClass('my1', 1, 0, parent=my0)
    >>> my2 = MyClass('my2', 0, 2, parent=my0)

    >>> for pre, _, node in RenderTree(my0):
    ...     treestr = u"%s%s" % (pre, node.name)
    ...     print(treestr.ljust(8), node.tree_length, node.tree_width)
    my0      0 0
    ├── my1  1 0
    └── my2  0 2

    Construction via `children`:

    >>> my0 = MyClass('my0', 0, 0, children=[
    ...     MyClass('my1', 1, 0),
    ...     MyClass('my2', 0, 2),
    ... ]

    >>> for pre, _, node in RenderTree(my0):
    ...     treestr = u"%s%s" % (pre, node.name)
    ...     print(treestr.ljust(8), node.tree_length, node.tree_width)
    my0      0 0
    ├── my1  1 0
    └── my2  0 2

    Both approaches can be mixed:

    >>> my0 = MyClass('my0', 0, 0, children=[
    ...     MyClass('my1', 1, 0),
    ... ]
    >>> my2 = MyClass('my2', 0, 2, parent=my0)

    >>> for pre, _, node in RenderTree(my0):
    ...     treestr = u"%s%s" % (pre, node.name)
    ...     print(treestr.ljust(8), node.tree_length, node.tree_width)
    my0      0 0
    ├── my1  1 0
    └── my2  0 2
    """

    @property
    def name(self) -> Optional[str]:
        try:
            return self.__name
        except AttributeError:
            self.__name = None
            return self.__name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Name should be a string.")
        if self.tree_parent is not None:
            if hasattr(self.tree_parent, self.name) and getattr(self.tree_parent, self.name) == self:
                delattr(self.tree_parent, self.name)
            if not hasattr(self.tree_parent, value):
                setattr(self.tree_parent, value, self)
        self.__name = value
        self._post_name_change(value)

    def _post_name_change(self, value: Any):
        """Method called after changing the name."""
        pass

    @property
    def tree_parent(self) -> Optional["Asset"]:
        """
        Parent Node.

        On set, the node is detached from any previous parent node and attached
        to the new node.

        >>> from anytree import Node, RenderTree
        >>> udo = Node("Udo")
        >>> marc = Node("Marc")
        >>> lian = Node("Lian", parent=marc)
        >>> print(RenderTree(udo))
        Node('/Udo')
        >>> print(RenderTree(marc))
        Node('/Marc')
        └── Node('/Marc/Lian')

        **Attach**

        >>> marc.tree_parent = udo
        >>> print(RenderTree(udo))
        Node('/Udo')
        └── Node('/Udo/Marc')
            └── Node('/Udo/Marc/Lian')

        **Detach**

        To make a node to a root node, just set this attribute to `None`.

        >>> marc.tree_is_root
        False
        >>> marc.tree_parent = None
        >>> marc.tree_is_root
        True
        """
        try:
            return self.__parent
        except AttributeError:
            return None

    @tree_parent.setter
    def tree_parent(self, value: "Asset"):
        if value is not None and not isinstance(value, NodeMixin):
            msg = "Parent node %r is not of type 'NodeMixin'." % value
            raise TreeError(msg)
        try:
            parent = self.__parent
        except AttributeError:
            parent = None
        if parent is not value:
            self.__check_loop(value)
            self.__detach(parent)
            self.__attach(value)

    def __check_loop(self, node: "Asset"):
        if node is not None:
            if node is self:
                msg = "Cannot set parent. %r cannot be parent of itself."
                raise LoopError(msg % self)
            if any(child is self for child in node.tree_iter_path_reverse()):
                msg = "Cannot set parent. %r is parent of %r."
                raise LoopError(msg % (self, node))

    def __detach(self, parent: "Asset"):
        if parent is not None:
            self._pre_detach_parent(parent)
            parentchildren = parent.__children_or_empty
            assert any(child is self for child in parentchildren), "Tree is corrupt."  # pragma: no cover

            # ATOMIC START
            parent.__children = [child for child in parentchildren if child is not self]
            self.__parent = None
            # ATOMIC END

            # We remove the attributes associated to the previous parent if needed
            if hasattr(self.tree_parent, self.name) and getattr(self.tree_parent, self.name) == self:
                delattr(self.tree_parent, self.name)

            self._post_detach_parent(parent)

    def __attach(self, parent: "Asset"):
        if parent is not None:
            self._pre_attach_parent(parent)
            parentchildren = parent.__children_or_empty

            # Quite slow test
            # assert not any(child is self for child in parentchildren), "Tree is corrupt."  # pragma: no cover

            # ATOMIC START
            parentchildren.append(self)
            self.__parent = parent
            # ATOMIC END

            # We add name attribute associated to the new children if there is no attribute of this name.
            if not hasattr(parent, self.name):
                setattr(parent, self.name, self)

            self._post_attach_parent(parent)

    @property
    def __children_or_empty(self) -> List["Asset"]:
        try:
            return self.__children
        except AttributeError:
            self.__children = []
            return self.__children

    @property
    def tree_children(self) -> Tuple["Asset", ...]:
        """
        All child nodes.

        >>> from anytree import Node
        >>> n = Node("n")
        >>> a = Node("a", parent=n)
        >>> b = Node("b", parent=n)
        >>> c = Node("c", parent=n)
        >>> n.tree_children
        (Node('/n/a'), Node('/n/b'), Node('/n/c'))

        Modifying the children attribute modifies the tree.

        **Detach**

        The children attribute can be updated by setting to an iterable.

        >>> n.tree_children = [a, b]
        >>> n.tree_children
        (Node('/n/a'), Node('/n/b'))

        Node `c` is removed from the tree.
        In case of an existing reference, the node `c` does not vanish and is the root of its own tree.

        >>> c
        Node('/c')

        **Attach**

        >>> d = Node("d")
        >>> d
        Node('/d')
        >>> n.tree_children = [a, b, d]
        >>> n.tree_children
        (Node('/n/a'), Node('/n/b'), Node('/n/d'))
        >>> d
        Node('/n/d')

        **Duplicate**

        A node can just be the children once. Duplicates cause a :any:`TreeError`:

        >>> n.tree_children = [a, b, d, a]
        Traceback (most recent call last):
            ...
        anytree.node.exceptions.TreeError: Cannot add node Node('/n/a') multiple times as child.
        """
        return tuple(self.__children_or_empty)

    @staticmethod
    def __check_children(children: Tuple["Asset", ...]):
        seen = set()
        for child in children:
            if not isinstance(child, NodeMixin):
                msg = "Cannot add non-node object %r. It is not a subclass of 'NodeMixin'." % child
                raise TreeError(msg)
            childid = id(child)
            if childid not in seen:
                seen.add(childid)
            else:
                msg = "Cannot add node %r multiple times as child." % child
                raise TreeError(msg)

    @tree_children.setter
    def tree_children(self, children: Tuple["Asset", ...]):
        # convert iterable to tuple
        children = tuple(children)
        NodeMixin.__check_children(children)
        # ATOMIC start
        old_children = self.tree_children
        del self.tree_children
        try:
            self._pre_attach_children(children)
            for child in children:
                child.tree_parent = self

            # We add name attributes associated to the children if there is no attribute of this name.
            for child in children:
                if not hasattr(self, child.name):
                    setattr(self, child.name, child)

            self._post_attach_children(children)
            assert len(self.tree_children) == len(children)
        except Exception:
            self.tree_children = old_children
            raise
        # ATOMIC end

    @tree_children.deleter
    def tree_children(self):
        children = self.tree_children
        self._pre_detach_children(children)
        for child in self.tree_children:
            child.tree_parent = None
        assert len(self.tree_children) == 0

        #  We remove the attributes associated to the children if needed.
        for child in children:
            if hasattr(self, child.name) and getattr(self, child.name) == child:
                delattr(self, child.name)

        self._post_detach_children(children)

    def _pre_detach_children(self, children: Tuple["Asset", ...]):
        """Method call before detaching `children`."""
        pass

    def _pre_attach_children(self, children: Tuple["Asset", ...]):
        """Method call before attaching `children`."""
        pass

    def _post_detach_children(self, children: Tuple["Asset", ...]):
        """Method call after detaching `children`"""
        pass

    def _post_attach_children(self, children: Tuple["Asset", ...]):
        """Method call after attaching `children`."""
        pass

    def _pre_detach_parent(self, parent: "Asset"):
        """Method call before detaching from `parent`."""
        pass

    def _pre_attach_parent(self, parent: "Asset"):
        """Method call when attaching to `parent`."""
        pass

    def _post_detach_parent(self, parent: "Asset"):
        """Method call before attaching to `parent`."""
        pass

    def _post_attach_parent(self, parent: "Asset"):
        """Method call after attaching to `parent`."""
        pass

    def remove(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        if isinstance(assets, NodeMixin):
            assets.tree_parent = None
        else:
            for asset in assets:
                asset.tree_parent = None
        return self

    def add(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        if isinstance(assets, NodeMixin):
            assets.tree_parent = self
        else:
            for asset in assets:
                asset.tree_parent = self
        return self

    def __iadd__(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        return self.add(assets)

    def __add__(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        return self.add(assets)

    def __isub__(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        return self.remove(assets)

    def __sub__(self, assets: Union["Asset", Sequence["Asset"]]) -> "NodeMixin":
        return self.remove(assets)

    def _get_one_line_repr(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        node_str = self._get_one_line_repr() + ("\n" if self.tree_children else "")
        return f"{node_str}{RenderTree(self).print_tree()}"

    def tree_filtered_descendants(
        self, filter_fn: Callable[["Asset"], bool], stop=None, maxlevel: Optional[int] = None
    ) -> Tuple["Asset", ...]:
        """
        Iterate over tree starting at node.
        Keyword Args:
            filter_fn: function called with every node as argument, node is returned if True.
            stop: stop iteration at node if stop function returns True for node.
            maxlevel (int): maximum descending in the node hierarchy.
        """
        return tuple(PreOrderIter(self, filter_=filter_fn, stop=stop, maxlevel=maxlevel))

    @property
    def tree_path(self) -> Tuple["Asset", ...]:
        """
        Path of this `Node`.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_path
        (Node('/Udo'),)
        >>> marc.tree_path
        (Node('/Udo'), Node('/Udo/Marc'))
        >>> lian.tree_path
        (Node('/Udo'), Node('/Udo/Marc'), Node('/Udo/Marc/Lian'))
        """
        return self._path

    def tree_iter_path_reverse(self) -> Iterator["Asset"]:
        """
        Iterate up the tree from the current node.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> for node in udo.tree_iter_path_reverse():
        ...     print(node)
        Node('/Udo')
        >>> for node in marc.tree_iter_path_reverse():
        ...     print(node)
        Node('/Udo/Marc')
        Node('/Udo')
        >>> for node in lian.tree_iter_path_reverse():
        ...     print(node)
        Node('/Udo/Marc/Lian')
        Node('/Udo/Marc')
        Node('/Udo')
        """
        node = self
        while node is not None:
            yield node
            node = node.tree_parent

    def __iter__(self) -> Iterator["Asset"]:
        return PreOrderIter(self)

    @property
    def _path(self) -> Tuple["Asset", ...]:
        return tuple(reversed(list(self.tree_iter_path_reverse())))

    @property
    def tree_ancestors(self) -> Tuple["Asset", ...]:
        """
        All parent nodes and their parent nodes.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_ancestors
        ()
        >>> marc.tree_ancestors
        (Node('/Udo'),)
        >>> lian.tree_ancestors
        (Node('/Udo'), Node('/Udo/Marc'))
        """
        if self.tree_parent is None:
            return tuple()
        return self.tree_parent.tree_path

    @property
    def tree_descendants(self) -> Tuple["Asset", ...]:
        """
        All child nodes and all their child nodes.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> loui = Node("Loui", parent=marc)
        >>> soe = Node("Soe", parent=lian)
        >>> udo.tree_descendants
        (Node('/Udo/Marc'), Node('/Udo/Marc/Lian'), Node('/Udo/Marc/Lian/Soe'), Node('/Udo/Marc/Loui'))
        >>> marc.tree_descendants
        (Node('/Udo/Marc/Lian'), Node('/Udo/Marc/Lian/Soe'), Node('/Udo/Marc/Loui'))
        >>> lian.tree_descendants
        (Node('/Udo/Marc/Lian/Soe'),)
        """
        return tuple(PreOrderIter(self))[1:]

    @property
    def tree_root(self) -> "Asset":
        """
        Tree Root Node.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_root
        Node('/Udo')
        >>> marc.tree_root
        Node('/Udo')
        >>> lian.tree_root
        Node('/Udo')
        """
        node = self
        while node.tree_parent is not None:
            node = node.tree_parent
        return node

    @property
    def tree_siblings(self) -> Tuple["Asset", ...]:
        """
        Tuple of nodes with the same parent.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> loui = Node("Loui", parent=marc)
        >>> lazy = Node("Lazy", parent=marc)
        >>> udo.tree_siblings
        ()
        >>> marc.tree_siblings
        ()
        >>> lian.tree_siblings
        (Node('/Udo/Marc/Loui'), Node('/Udo/Marc/Lazy'))
        >>> loui.tree_siblings
        (Node('/Udo/Marc/Lian'), Node('/Udo/Marc/Lazy'))
        """
        parent = self.tree_parent
        if parent is None:
            return tuple()
        else:
            return tuple(node for node in parent.tree_children if node is not self)

    @property
    def tree_leaves(self) -> Tuple["Asset", ...]:
        """
        Tuple of all leaf nodes.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> loui = Node("Loui", parent=marc)
        >>> lazy = Node("Lazy", parent=marc)
        >>> udo.tree_leaves
        (Node('/Udo/Marc/Lian'), Node('/Udo/Marc/Loui'), Node('/Udo/Marc/Lazy'))
        >>> marc.tree_leaves
        (Node('/Udo/Marc/Lian'), Node('/Udo/Marc/Loui'), Node('/Udo/Marc/Lazy'))
        """
        return tuple(PreOrderIter(self, filter_=lambda node: node.tree_is_leaf))

    @property
    def tree_is_leaf(self) -> bool:
        """
        `Node` has no children (External Node).

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_is_leaf
        False
        >>> marc.tree_is_leaf
        False
        >>> lian.tree_is_leaf
        True
        """
        return len(self.__children_or_empty) == 0

    @property
    def tree_is_root(self) -> bool:
        """
        `Node` is tree root.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_is_root
        True
        >>> marc.tree_is_root
        False
        >>> lian.tree_is_root
        False
        """
        return self.tree_parent is None

    @property
    def tree_height(self) -> int:
        """
        Number of edges on the longest path to a leaf `Node`.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_height
        2
        >>> marc.tree_height
        1
        >>> lian.tree_height
        0
        """
        children = self.__children_or_empty
        if children:
            return max(child.tree_height for child in children) + 1
        else:
            return 0

    @property
    def tree_depth(self) -> int:
        """
        Number of edges to the root `Node`.

        >>> from anytree import Node
        >>> udo = Node("Udo")
        >>> marc = Node("Marc", parent=udo)
        >>> lian = Node("Lian", parent=marc)
        >>> udo.tree_depth
        0
        >>> marc.tree_depth
        1
        >>> lian.tree_depth
        2
        """
        i = 0
        # count without storing the entire path
        for i, _ in enumerate(self.tree_iter_path_reverse()):
            continue
        return i
