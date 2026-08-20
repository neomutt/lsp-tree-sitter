r"""Node
========
"""

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from shlex import split

from lsprotocol.types import Position, Range
from tree_sitter import Node


class NodeText(str):
    r"""Node text."""

    def __new__(cls, node: Node | None) -> str:
        r"""New.

        :param cls:
        :param node:
        :type node: Node | None
        :rtype: str
        """
        if node is None:
            return ""
        return node.text.decode() if node.text else ""


class NodeTuples(tuple[tuple[int, int], tuple[int, int]]):
    r"""Node tuples."""

    def __new__(
        cls, node: Node | None
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        r"""New.

        :param cls:
        :param node:
        :type node: Node | None
        :rtype: tuple[tuple[int, int], tuple[int, int]]
        """
        if node is None:
            return (-1, -1), (-1, -1)
        return tuple(node.start_point), tuple(node.end_point)


class NodeDict(dict):
    r"""Node dict."""

    @classmethod
    def from_node(cls, node: Node | None) -> dict:
        r"""Factory function from node.

        :param cls:
        :param node:
        :type node: Node | None
        :rtype: dict
        """
        return {
            "type": node.type if node else "",
            "text": NodeText(node),
            "range": NodeTuples(node),
        }


class NodeRange(Range):
    r"""Node range."""

    @classmethod
    def from_node(cls, node: Node) -> Range:
        r"""Factory function from node.

        :param cls:
        :param node:
        :type node: Node
        :rtype: Range
        """
        return cls.from_tuples(NodeTuples(node))

    @classmethod
    def from_tuples(
        cls, tup: tuple[tuple[int, int], tuple[int, int]]
    ) -> Range:
        r"""Factory function from tuples.

        :param cls:
        :param tup:
        :type tup: tuple[tuple[int, int], tuple[int, int]]
        :rtype: Range
        """
        return cls(Position(*tup[0]), Position(*tup[1]))


class NodeOps(list[str]):
    r"""Node operations.

    - ``^`` means parent node
    - ``+`` means next sibling node
    - ``-`` means previous sibling node
    - ``n`` means the n-th child node (0-based index)
    """

    regex: re.Pattern = re.compile(r"([-+^]|\d+)")

    @classmethod
    def from_str(cls, code: str) -> "NodeOps":
        r"""Factory function from str.

        :param cls:
        :param code:
        :type code: str
        :rtype: NodeOps
        """
        return cls(cls.regex.findall(code))

    def __call__(self, node: Node | None) -> Node | None:
        r"""Operate node to get a new node.

        :param self:
        :param node:
        :type node: Node | None
        :rtype: Node | None
        """
        for op in self:
            match op:
                case "^":
                    node = node.parent if node else None
                case "+":
                    node = node.next_sibling if node else None
                case "-":
                    node = node.prev_sibling if node else None
                case x:
                    node = node.child(int(x)) if node else None
        return node


@dataclass
class NodeFilter:
    r"""Node filter."""

    texts: tuple[str, ...] = ()
    kind: str = "variable_name"
    selector: str = "^--"

    def __call__(self, node: Node | None) -> bool:
        r"""Judge whether the node is a match.

        :param self:
        :param node:
        :type node: Node | None
        :rtype: bool
        """
        node = NodeOps.from_str(self.selector)(node)
        return (
            node is not None
            and node.type == self.kind
            and (NodeText(node) in self.texts if self.texts else True)
        )


@dataclass
class PackageSearcher(NodeFilter):
    r"""Package searcher."""

    label: str = "package"

    def has_package(self, name: str) -> bool:
        r"""Has package.

        :param self:
        :param name:
        :type name: str
        :rtype: bool
        """
        raise NotImplementedError

    def get_package_url(self, name: str) -> str:
        r"""For textDocument/link.

        :param self:
        :param name:
        :type name: str
        :rtype: str
        """
        raise NotImplementedError

    def get_package_version(self, name: str) -> str:
        r"""For textDocument/inlayHint.

        :param self:
        :param name:
        :type name: str
        :rtype: str
        """
        raise NotImplementedError

    def get_package_document(self, name: str) -> str:
        r"""For textDocument/hover.

        :param self:
        :param name:
        :type name: str
        :rtype: str
        """
        raise NotImplementedError

    def get_package_names(self, name: str) -> dict[str, str]:
        r"""For textDocument/completion.

        :param self:
        :param name:
        :type name: str
        :rtype: dict[str, str]
        """
        raise NotImplementedError

    @staticmethod
    def get_filetype(path: str, filetypes: Iterable[str]) -> str | None:
        r"""Get filetype.

        :param path:
        :type path: str
        :param filetypes:
        :type filetypes: Iterable[str]
        :rtype: str | None
        """
        basename = os.path.basename(path)
        for filetype in filetypes:
            if (
                basename.endswith("." + filetype[1:])
                if filetype.startswith("_")
                else basename == filetype
            ):
                return filetype
        return ""

    @staticmethod
    def get_package_name(name: str) -> str:
        r"""Get the package name from the text.
        e.g. "package>=0.0.1" -> "package".

        :param name:
        :type name: str
        :rtype: str
        """
        name = split(name)[0]
        for sep in ":><=!":
            name = name.partition(sep)[0]
        return name.strip()
