r"""Schema
==========
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

from lsprotocol.types import Position, Range
from tree_sitter import Node, Tree

from . import UNI


@dataclass
class Trie:
    r"""Trie."""

    range: Range
    parent: Self | None = None
    # can be serialized to a json
    value: dict[str, Self] | list[Self] | str | int | float | None = None

    @property
    def root(self) -> Self:
        r"""Get root: all ``Trie`` 's ancestor.

        :rtype: Self
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def __str__(self) -> str:
        r"""Convert a ``Trie`` to a jq expression.

        :rtype: str
        """
        if self.parent is None:
            return "$"
        path = str(self.parent)
        if isinstance(self.parent.value, dict):
            for k, v in self.parent.value.items():
                if v is self:
                    return f"{path}.{k}"
            raise TypeError
        if isinstance(self.parent.value, list):
            for k, v in enumerate(self.parent.value):
                if v is self:
                    return f"{path}[{k}]"
            raise TypeError
        return path

    def __getitem__(self, path: str) -> Self:
        r"""Get a ``Trie`` by a jq expression.

        :param path:
        :type path: str
        :rtype: Self
        """
        node = self
        if path.startswith("$"):
            path = path.lstrip("$")
            node = self.root
        if path == "":
            return node
        if path.startswith("."):
            if not isinstance(node.value, dict):
                raise TypeError
            path = path.lstrip(".")
            index, mid, path = path.partition(".")
            if mid == ".":
                path = mid + path
            index, mid, suffix = index.partition("[")
            if mid == "[":
                path = mid + suffix + path
            return node.value[index][path]
        if path.startswith("["):
            if not isinstance(node.value, list):
                raise TypeError
            path = path.lstrip("[")
            index, _, path = path.partition("]")
            index = int(index)
            return node.value[index][path]
        raise TypeError

    def to_json(self) -> dict[str, Any] | list[Any] | str | int | float | None:
        r"""To json.

        :rtype: dict[str, Any] | list[Any] | str | int | float | None
        """
        if isinstance(self.value, dict):
            return {k: v.to_json() for k, v in self.value.items()}
        if isinstance(self.value, list):
            return [v.to_json() for v in self.value]
        return self.value

    @classmethod
    def from_tree(cls, tree: Tree) -> Self:
        r"""From tree.

        :param tree:
        :type tree: Tree
        :rtype: Self
        """
        return cls.from_node(tree.root_node, None)

    @classmethod
    def from_file(cls, file: str, parse: Callable[[bytes], Tree]) -> Self:
        r"""From file.

        :param file:
        :type file: str
        :param parse:
        :type parse: Callable[[bytes], Tree]
        :rtype: Self
        """
        with open(file, "rb") as f:
            text = f.read()
        return cls.from_tree(parse(text))

    @classmethod
    def from_node(cls, node: Node, parent: Self | None) -> Self:
        r"""From node.

        :param node:
        :type node: Node
        :param parent:
        :type parent: Self | None
        :rtype: Self
        """
        if parent is None:
            _range = Range(Position(0, 0), Position(1, 0))
        else:
            _range = UNI(node).range
        trie = cls(_range, parent, {})
        trie.value = {
            UNI(child.children[0]).text: cls.from_node(child, trie)
            for child in node.children
        }
        return trie
