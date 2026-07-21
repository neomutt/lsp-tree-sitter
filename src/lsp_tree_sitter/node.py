r"""Node
========
"""

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass

from lsprotocol.types import Position, Range
from tree_sitter import Node


class NodeText(str):
    def __new__(cls, node: Node | None) -> str:
        if node is None:
            return ""
        return node.text.decode() if node.text else ""


class NodeTuples(tuple[tuple[int, int], tuple[int, int]]):
    def __new__(
        cls, node: Node | None
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        if node is None:
            return (-1, -1), (-1, -1)
        return tuple(node.start_point), tuple(node.end_point)


class NodeRange:
    def __new__(cls, node: Node) -> Range:
        return cls.from_tuples(NodeTuples(node))

    @staticmethod
    def from_tuples(tup: tuple[tuple[int, int], tuple[int, int]]) -> Range:
        return Range(Position(*tup[0]), Position(*tup[1]))


class NodeOps(list[str]):
    regex: re.Pattern = re.compile(r"([-+^]|\d+)")

    @classmethod
    def from_str(cls, code: str) -> "NodeOps":
        return cls(cls.regex.findall(code))

    def __call__(self, node: Node | None) -> Node | None:
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
    texts: tuple[str, ...] = ()
    kind: str = "variable_name"
    selector: str = "^-"

    def __call__(self, node: Node | None) -> bool:
        node = NodeOps.from_str(self.selector)(node)
        return (
            node is not None
            and node.type == self.kind
            and (NodeText(node) in self.texts if self.texts else True)
        )


@dataclass
class PackageSearcher(NodeFilter):
    label: str = "package"

    def has_package(self, name: str) -> bool:
        return self.get_package_document(name) is not None

    def get_package_url(self, name: str) -> str:
        r"""For textDocument/link"""
        raise NotImplementedError

    def get_package_document(self, name: str) -> str:
        r"""For textDocument/hover"""
        raise NotImplementedError

    def get_package_names(self, name: str) -> dict[str, str]:
        r"""For textDocument/completion"""
        raise NotImplementedError

    @staticmethod
    def get_filetype(path: str, filetypes: Iterable[str]) -> str | None:
        basename = os.path.basename(path)
        for filetype in filetypes:
            if (
                basename.endswith("." + filetype[1:])
                if filetype.startswith("_")
                else basename == filetype
            ):
                return filetype
        return ""
