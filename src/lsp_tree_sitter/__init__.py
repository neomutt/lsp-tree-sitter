r"""LSP Tree sitter
===================
"""

import os
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self

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
from pygls.uris import to_fs_path
from tree_sitter import Node, Tree, TreeCursor

try:
    from ._version import __version__, __version_tuple__  # type: ignore
except ImportError:  # for setuptools-generate
    __version__ = "rolling"
    __version_tuple__ = (0, 0, 0, __version__, "")


@dataclass
class UNI:
    r"""Unified node identifier.

    ``uri`` and ``path`` is document's uri and path.
    """

    node: Node
    uri: str = ""

    def __str__(self) -> str:
        r"""Str.

        :rtype: str
        """
        return (
            f"{self.text}@{self.uri}:"
            f"{self.node.start_point[0] + 1}:{self.node.start_point[1] + 1}-"
            f"{self.node.end_point[0] + 1}:{self.node.end_point[1]}"
        )

    @property
    def text(self) -> str:
        r"""Text.

        :rtype: str
        """
        return self.node.text.decode() if self.node.text else ""

    @property
    def filepath(self) -> str:
        r"""Filepath.

        :param self:
        :rtype: str
        """
        filepath = to_fs_path(self.uri)
        if filepath is None:
            raise TypeError
        return filepath

    @property
    def path(self) -> str:
        r"""Path.

        :rtype: str
        """
        text = os.path.expandvars(os.path.expanduser(self.text))
        return os.path.join(os.path.dirname(self.filepath), text)

    @property
    def range(self) -> Range:
        r"""Range.

        :rtype: Range
        """
        return Range(
            Position(*self.node.start_point), Position(*self.node.end_point)
        )

    @property
    def location(self) -> Location:
        r"""Location.

        :rtype: Location
        """
        return Location(self.uri, self.range)

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
            self.range,
            Template(message).render(uni=self, **kwargs),
            severity,
        )

    def get_text_edit(self, new_text: str) -> TextEdit:
        r"""Get text edit.

        :param new_text:
        :type new_text: str
        :rtype: TextEdit
        """
        return TextEdit(self.range, new_text)

    def get_document_link(
        self, target: str = "{{uni.uri}}", **kwargs: Any
    ) -> DocumentLink:
        r"""Get document link.

        :param target:
        :type target: str
        :param kwargs:
        :type kwargs: Any
        :rtype: DocumentLink
        """
        return DocumentLink(
            self.range,
            Template(target).render(uni=self, **kwargs),
        )


@dataclass
class Finder:
    r"""Finder."""

    message: str = ""
    severity: DiagnosticSeverity = DiagnosticSeverity.Error
    max_level: int = 5
    level: int = 0
    unis: list[UNI] = field(default_factory=list)

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return True

    def __and__(self, second: Self) -> "AndFinder":
        r"""And.

        :param second:
        :type second: Self
        :rtype: AndFinder
        """
        return AndFinder(finders=(self, second))

    def __or__(self, second: Self) -> "OrFinder":
        r"""Or.

        :param second:
        :type second: Self
        :rtype: OrFinder
        """
        return OrFinder(finders=(self, second))

    def __minus__(self, second: Self) -> "AndFinder":
        r"""Minus.

        :param second:
        :type second: Self
        :rtype: AndFinder
        """
        return AndFinder(finders=(self, NotFinder(finder=second)))

    def __invert__(self) -> "NotFinder":
        r"""Invert.

        :rtype: NotFinder
        """
        return NotFinder(finder=self)

    def __enter__(self) -> None:
        self.level += 1

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.level -= 1

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
        path = to_fs_path(uri)
        if path is None:
            raise TypeError
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            code = f.read()
        return self.parse(code)

    def uni2uri(self, uni: UNI) -> str:
        r"""Convert UNI to node's URI. Used by ``move_cursor()`` to parse
        recursively. Override it if necessary. *Visitor pattern*.

        :param uni:
        :type uni: UNI
        :rtype: str
        """
        return uni.uri

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
        if cursor.node is None:
            raise TypeError
        while self(UNI(cursor.node, uri)) is False:
            if (
                self.is_include_node(cursor.node)
                and self.level < self.max_level
            ):
                uni = UNI(cursor.node, uri)
                new_uri = self.uni2uri(uni)
                tree = self.uri2tree(new_uri)
                # skip if cannot convert `uni`'s `include_node` to a tree
                if tree is not None:
                    with self:
                        if is_all:
                            # don't `self.reset()` to use `self.unis` again
                            self.find_all(new_uri, tree, False)
                        else:
                            result = self.find(new_uri, tree)
                            if result is not None:
                                return new_uri
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
        if cursor.node is None:
            raise TypeError
        _uri = self.move_cursor(uri, cursor, False)
        if _uri is not None:
            return UNI(cursor.node, _uri)

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
        if cursor.node is None:
            raise TypeError
        while True:
            _uri = self.move_cursor(uri, cursor, True)
            if _uri is not None:
                self.unis += [UNI(cursor.node, _uri)]
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return self.unis
            cursor.goto_next_sibling()

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
        self, uri: str, tree: Tree, template: str = "{{uni.uri}}"
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


@dataclass
class AndFinder(Finder):
    finders: tuple[Finder, ...] = ()

    def __call__(self, uni: UNI) -> bool:
        return all(finder(uni) for finder in self.finders)


@dataclass
class OrFinder(Finder):
    finders: tuple[Finder, ...] = ()

    def __call__(self, uni: UNI) -> bool:
        return any(finder(uni) for finder in self.finders)


@dataclass
class NotFinder(Finder):
    finder: Finder = field(default_factory=Finder)

    def __call__(self, uni: UNI) -> bool:
        return not self.finder(uni)
