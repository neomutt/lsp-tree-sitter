r"""LSP Tree-sitter
===================
"""

import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from jinja2 import Template
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    DocumentLink,
    Location,
    Position,
    Range,
    TextEdit,
)
from pygls.uris import from_fs_path, to_fs_path
from tree_sitter import Node, Tree, TreeCursor

try:
    from ._version import __version__, __version_tuple__  # type: ignore
except ImportError:  # for setuptools-generate
    __version__ = "rolling"
    __version_tuple__ = (0, 0, 0, __version__, "")

# maximum of recursive search
LEVEL = 5


@dataclass
class UNI:
    r"""Unified node identifier.

    ``uri`` and ``path`` is document's uri and path.
    ``get_uri()`` and ``get_path()`` is node's uri and path which are
    calculated by ``uri`` and ``path``, can throw ``TypeError`` when ``uri`` is
    wrong. ``path`` can be ``None`` for wrong ``uri``.
    """

    uri: str
    node: Node

    def __post_init__(self):
        if urlparse(self.uri).scheme == "":
            self.path = self.uri
            self.uri = from_fs_path(self.path)
        else:
            self.path = to_fs_path(self.uri)

    def __str__(self) -> str:
        r"""Str.

        :rtype: str
        """
        return (
            f"{self.get_text()}@{self.uri}:"
            f"{self.node.start_point[0] + 1}:{self.node.start_point[1] + 1}-"
            f"{self.node.end_point[0] + 1}:{self.node.end_point[1]}"
        )

    def get_text(self) -> str:
        r"""Get text.

        :rtype: str
        """
        return self.node2text(self.node)

    @staticmethod
    def node2text(node: Node) -> str:
        r"""Node2text.

        :param node:
        :type node: Node
        :rtype: str
        """
        return node.text.decode()

    def get_location(self) -> Location:
        r"""Get location.

        :rtype: Location
        """
        return Location(self.uri, self.get_range())

    def get_range(self) -> Range:
        r"""Get range.

        :rtype: Range
        """
        return self.node2range(self.node)

    @staticmethod
    def node2range(node: Node) -> Range:
        r"""Node2range.

        :param node:
        :type node: Node
        :rtype: Range
        """
        return Range(Position(*node.start_point), Position(*node.end_point))

    @staticmethod
    def uri2path(uri: str) -> str:
        r"""Uri2path.

        :param uri:
        :type uri: str
        :rtype: str
        """
        if path := to_fs_path(uri):
            return path
        raise TypeError

    @staticmethod
    def path2uri(path: str) -> str:
        r"""Path2uri.

        :param path:
        :type path: str
        :rtype: str
        """
        if uri := from_fs_path(path):
            return uri
        raise TypeError

    def get_path(self) -> str:
        r"""Get path.

        :rtype: str
        """
        if self.path is None:
            raise TypeError
        text = os.path.expandvars(os.path.expanduser(self.get_text()))
        return self.join(self.path, text)

    def get_uri(self) -> str:
        r"""Get uri.

        :rtype: str
        """
        return self.path2uri(self.get_path())

    @staticmethod
    def join(path, text) -> str:
        r"""Join document's path and text to get node's path.

        :param path:
        :param text:
        :rtype: str
        """
        return os.path.join(os.path.dirname(path), text)

    def get_diagnostic(
        self,
        message: str,
        severity: DiagnosticSeverity,
        **kwargs: Any,
    ) -> Diagnostic:
        r"""Get diagnostic.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :param kwargs:
        :type kwargs: Any
        :rtype: Diagnostic
        """
        return Diagnostic(
            self.get_range(),
            Template(message).render(uni=self, **kwargs),
            severity,
        )

    def get_text_edit(self, new_text: str) -> TextEdit:
        r"""Get text edit.

        :param new_text:
        :type new_text: str
        :rtype: TextEdit
        """
        return TextEdit(self.get_range(), new_text)

    def get_document_link(
        self, target: str = "{{uni.get_uri()}}", **kwargs
    ) -> DocumentLink:
        r"""Get document link.

        :param target:
        :type target: str
        :param kwargs:
        :rtype: DocumentLink
        """
        return DocumentLink(
            self.get_range(),
            Template(target).render(uni=self, **kwargs),
        )


@dataclass
class Finder:
    r"""Finder."""

    message: str = ""
    severity: DiagnosticSeverity = DiagnosticSeverity.Error

    def __post_init__(self) -> None:
        r"""Post init.

        :rtype: None
        """
        self.reset()

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return True

    def __and__(self, second: "Finder") -> "Finder":
        r"""And.

        :param second:
        :type second: Finder
        :rtype: "Finder"
        """
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) and second(uni)
        return finder

    def __or__(self, second: "Finder") -> "Finder":
        r"""Or.

        :param second:
        :type second: Finder
        :rtype: "Finder"
        """
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) or second(uni)
        return finder

    def __minus__(self, second: "Finder") -> "Finder":
        r"""Minus.

        :param second:
        :type second: Finder
        :rtype: "Finder"
        """
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) and not second(uni)
        return finder

    def is_include_node(self, node: Node) -> bool:
        r"""Is include node.

        :param node:
        :type node: Node
        :rtype: bool
        """
        return False

    def parse(self, code: bytes) -> Tree:
        r"""Parse.

        :param code:
        :type code: bytes
        :rtype: Tree
        """
        raise NotImplementedError

    def uri2tree(self, uri: str) -> Tree | None:
        r"""Convert ``uri`` to ``Tree``. Used by ``prepare()``,
        ``move_cursor()``.

        :param uri:
        :type uri: str
        :rtype: Tree | None
        """
        path = UNI.uri2path(uri)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            code = f.read()
        return self.parse(code)

    def uni2uri(self, uni: UNI) -> str:
        r"""Convert UNI to node's URI. Used by ``move_cursor()`` to parse
        recursively. Override it if necessary.

        :param uni:
        :type uni: UNI
        :rtype: str
        """
        return uni.get_uri()

    def move_cursor(
        self, uri: str, cursor: TreeCursor, is_all: bool = False
    ) -> str | None:
        r"""Move cursor to next ``UNI``'s ``node`` which can make
        ``self.__call__()`` return ``True``. Then return ``UNI``'s ``uri``. If
        ``self.is_include_node()`` always be ``False``, returned inputted
        ``uri``. If no any ``UNI``'s ``node`` which can make ``self.__call__()
        `` return ``True``, return ``None``.

        :param self:
        :param uri:
        :type uri: str
        :param cursor:
        :type cursor: TreeCursor
        :param is_all:
        :type is_all: bool
        :rtype: str | None
        """
        while self(UNI(uri, cursor.node)) is False:
            if self.is_include_node(cursor.node) and self.level < LEVEL:
                self.level += 1
                # push current uri
                old_uri = uri
                uni = UNI(uri, cursor.node)
                # update new uri
                uri = self.uni2uri(uni)
                tree = self.uri2tree(uri)
                # skip if cannot convert ``uni``'s ``include_node`` to a tree.
                if tree is not None:
                    if is_all:
                        # don't ``self.reset()`` to use ``self.unis`` again.
                        self.find_all(uri, tree, False)
                    else:
                        result = self.find(uri, tree)
                        if result is not None:
                            return uri
                # pop current uri
                uri = old_uri
                self.level -= 1
            if cursor.node.child_count > 0:
                cursor.goto_first_child()
                continue
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return None
            cursor.goto_next_sibling()
        return uri

    def reset(self) -> None:
        r"""Reset.

        :rtype: None
        """
        self.level = 0
        self.unis = []

    def prepare(
        self, uri: str, tree: Tree | None = None, reset: bool = True
    ) -> Tree:
        r"""Prepare.

        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree | None
        :param reset:
        :type reset: bool
        :rtype: Tree
        """
        if reset:
            self.reset()
        if tree is None:
            tree = self.uri2tree(uri)
        if tree is None:
            raise TypeError
        return tree

    def find(
        self, uri: str, tree: Tree | None = None, reset: bool = True
    ) -> UNI | None:
        r"""Find.

        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree | None
        :param reset:
        :type reset: bool
        :rtype: UNI | None
        """
        cursor = self.prepare(uri, tree, reset).walk()
        _uri = self.move_cursor(uri, cursor, False)
        if _uri is not None:
            return UNI(_uri, cursor.node)

    def find_all(
        self, uri: str, tree: Tree | None = None, reset: bool = True
    ) -> list[UNI]:
        r"""Find all.

        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree | None
        :param reset:
        :type reset: bool
        :rtype: list[UNI]
        """
        cursor = self.prepare(uri, tree, reset).walk()
        while True:
            _uri = self.move_cursor(uri, cursor, True)
            if _uri is not None:
                self.unis += [UNI(_uri, cursor.node)]
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return self.unis
            cursor.goto_next_sibling()

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        r"""Uni2diagnostic.

        :param uni:
        :type uni: UNI
        :rtype: Diagnostic
        """
        return uni.get_diagnostic(self.message, self.severity)

    def unis2diagnostics(self, unis: list[UNI]) -> list[Diagnostic]:
        r"""Unis2diagnostics.

        :param unis:
        :type unis: list[UNI]
        :rtype: list[Diagnostic]
        """
        return [self.uni2diagnostic(uni) for uni in unis]

    def get_diagnostics(self, uri: str, tree: Tree) -> list[Diagnostic]:
        r"""Get diagnostics.

        :param self:
        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree
        :rtype: list[Diagnostic]
        """
        return self.unis2diagnostics(self.find_all(uri, tree))

    def get_text_edits(self, uri: str, tree: Tree) -> list[TextEdit]:
        r"""Get text edits.

        :param self:
        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree
        :rtype: list[TextEdit]
        """
        self.find_all(uri, tree)
        return []

    def get_document_links(
        self, uri: str, tree: Tree, template: str = "{{uni.get_uri()}}"
    ) -> list[DocumentLink]:
        r"""Get document links.

        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree
        :param template:
        :type template: str
        :rtype: list[DocumentLink]
        """
        self.find_all(uri, tree)
        return [
            uni.get_document_link(template) for uni in self.find_all(uri, tree)
        ]
