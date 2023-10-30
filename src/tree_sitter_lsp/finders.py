r"""Finders
===========
"""
import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from jinja2 import Template
from jsonschema import Validator
from jsonschema.validators import validator_for
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    Position,
    Range,
    TextEdit,
)
from tree_sitter import Language, Node, Tree
from tree_sitter.binding import Query

from . import UNI, Finder
from .schema import Trie


@dataclass
class MissingFinder(Finder):
    r"""Missingfinder."""

    message: str = "{{uni.get_text()}}: missing"
    severity: DiagnosticSeverity = DiagnosticSeverity.Error

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        node = uni.node
        return node.is_missing and not (
            any(child.is_missing for child in node.children)
        )


@dataclass
class NotFileFinder(Finder):
    r"""NotFilefinder."""

    message: str = "{{uni.get_text()}}: no such file or directory"
    severity: DiagnosticSeverity = DiagnosticSeverity.Error

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        path = self.uni2path(uni)
        return not (os.path.isfile(path) or os.path.isdir(path))


@dataclass
class RepeatedFinder(Finder):
    r"""Repeatedfinder."""

    message: str = "{{uni.get_text()}}: is repeated on {{_uni}}"
    severity: DiagnosticSeverity = DiagnosticSeverity.Warning

    def reset(self) -> None:
        r"""Reset.

        :rtype: None
        """
        self.level = 0
        self.unis = []
        self._unis = []
        self.uni_pairs = []

    def filter(self, uni: UNI) -> bool:
        r"""Filter.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return True

    def compare(self, uni: UNI, _uni: UNI) -> bool:
        r"""Compare.

        :param uni:
        :type uni: UNI
        :param _uni:
        :type _uni: UNI
        :rtype: bool
        """
        return uni.node.text == _uni.node.text

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        if self.filter(uni) is False:
            return False
        for _uni in self._unis:
            if self.compare(uni, _uni):
                self.uni_pairs += [[uni, _uni]]
                return True
        self._unis += [uni]
        return False

    def get_definitions(self, uni: UNI) -> list[Location]:
        r"""Get definitions.

        :param uni:
        :type uni: UNI
        :rtype: list[Location]
        """
        for uni_, _uni in self.uni_pairs:
            # cache hit
            if uni == uni_:
                return [_uni.get_location()]
        return []

    def get_references(self, uni: UNI) -> list[Location]:
        r"""Get references.

        :param uni:
        :type uni: UNI
        :rtype: list[Location]
        """
        locations = []
        for uni_, _uni in self.uni_pairs:
            # cache hit
            if uni == _uni:
                locations += [uni_.get_location()]
        return locations

    def get_text_edits(self, uri: str, tree: Tree) -> list[TextEdit]:
        r"""Get text edits. Only return two to avoid `Overlapping edit`

        :param self:
        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree
        :rtype: list[TextEdit]
        """
        self.find_all(uri, tree)
        for uni, _uni in self.uni_pairs:
            # swap 2 unis
            return [
                uni.get_text_edit(_uni.get_text()),
                _uni.get_text_edit(uni.get_text()),
            ]
        return []

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        r"""Uni2diagnostic.

        :param uni:
        :type uni: UNI
        :rtype: Diagnostic
        """
        for uni_, _uni in self.uni_pairs:
            if uni == uni_:
                return uni.get_diagnostic(
                    self.message, self.severity, _uni=_uni
                )
        return uni.get_diagnostic(self.message, self.severity)


@dataclass
class UnsortedFinder(RepeatedFinder):
    r"""Unsortedfinder."""

    message: str = "{{uni.get_text()}}: is unsorted due to {{_uni}}"
    severity: DiagnosticSeverity = DiagnosticSeverity.Warning

    def compare(self, uni: UNI, _uni: UNI) -> bool:
        r"""Compare.

        :param uni:
        :type uni: UNI
        :param _uni:
        :type _uni: UNI
        :rtype: bool
        """
        return uni.node.text < _uni.node.text


@dataclass(init=False)
class UnFixedOrderFinder(RepeatedFinder):
    r"""Unfixedorderfinder."""

    def __init__(
        self,
        order: list[Any],
        message: str = "{{uni.get_text()}}: is unsorted due to {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        r"""Init.

        :param order:
        :type order: list[Any]
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.order = order

    def filter(self, uni: UNI) -> bool:
        r"""Filter.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return uni.get_text() in self.order

    def compare(self, uni: UNI, _uni: UNI) -> bool:
        r"""Compare.

        :param uni:
        :type uni: UNI
        :param _uni:
        :type _uni: UNI
        :rtype: bool
        """
        return self.order.index(uni.get_text()) < self.order.index(
            _uni.get_text()
        )


@dataclass(init=False)
class TypeFinder(Finder):
    r"""Typefinder."""

    def __init__(
        self,
        type: str,
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        r"""Init.

        :param type:
        :type type: str
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.type = type

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        node = uni.node
        return node.type == self.type


@dataclass(init=False)
class PositionFinder(Finder):
    r"""Positionfinder."""

    def __init__(
        self,
        position: Position,
        left_equal: bool = True,
        right_equal: bool = False,
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        r"""Init.

        :param position:
        :type position: Position
        :param left_equal:
        :type left_equal: bool
        :param right_equal:
        :type right_equal: bool
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.position = position
        self.left_equal = left_equal
        self.right_equal = right_equal

    @staticmethod
    def belong(
        position: Position,
        node: Node,
        left_equal: bool = True,
        right_equal: bool = False,
    ) -> bool:
        r"""Belong.

        :param position:
        :type position: Position
        :param node:
        :type node: Node
        :param left_equal:
        :type left_equal: bool
        :param right_equal:
        :type right_equal: bool
        :rtype: bool
        """
        if left_equal:
            left_flag = Position(*node.start_point) <= position
        else:
            left_flag = Position(*node.start_point) < position
        if right_equal:
            right_flag = position <= Position(*node.end_point)
        else:
            right_flag = position < Position(*node.end_point)
        return left_flag and right_flag

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        node = uni.node
        return node.child_count == 0 and self.belong(
            self.position, node, self.left_equal, self.right_equal
        )


@dataclass(init=False)
class RangeFinder(Finder):
    r"""Rangefinder."""

    def __init__(
        self,
        range: Range,
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        r"""Init.

        :param range:
        :type range: Range
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.range = range

    @staticmethod
    def equal(_range: Range, node: Node) -> bool:
        r"""Equal.

        :param _range:
        :type _range: Range
        :param node:
        :type node: Node
        :rtype: bool
        """
        return _range.start == Position(
            *node.start_point
        ) and _range.end == Position(*node.end_point)

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        node = uni.node
        return self.equal(self.range, node)


@dataclass(init=False)
class RequiresFinder(Finder):
    r"""Requiresfinder."""

    def __init__(
        self,
        requires: set[Any],
        message: str = "{{require}}: required",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param requires:
        :type requires: set[Any]
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        self.requires = requires
        # will call reset() which will call self.requires
        super().__init__(message, severity)

    def reset(self) -> None:
        r"""Reset.

        :rtype: None
        """
        self.level = 0
        self.unis = []
        self._requires = deepcopy(self.requires)

    def filter(self, uni: UNI, require: Any) -> bool:
        r"""Filter.

        :param uni:
        :type uni: UNI
        :param require:
        :type require: Any
        :rtype: bool
        """
        return False

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        found = set()
        for require in self._requires:
            if self.filter(uni, require):
                found |= {require}
        self._requires -= found
        return False

    def require2message(self, require: Any, **kwargs: Any) -> str:
        r"""Require2message.

        :param require:
        :type require: Any
        :param kwargs:
        :type kwargs: Any
        :rtype: str
        """
        return Template(self.message).render(
            uni=self, require=require, **kwargs
        )

    def get_diagnostics(self, uri: str, tree: Tree) -> list[Diagnostic]:
        r"""Get diagnostics.

        :param uri:
        :type uri: str
        :param tree:
        :type tree: Tree
        :rtype: list[Diagnostic]
        """
        self.find_all(uri, tree)
        return [
            Diagnostic(
                # If you want to specify a range that contains a line including
                # the line ending character(s) then use an end position
                # denoting the start of the next line
                Range(Position(0, 0), Position(1, 0)),
                self.require2message(i),
                self.severity,
            )
            for i in self._requires
        ]


@dataclass(init=False)
class SchemaFinder(Finder):
    r"""Schemafinder."""

    def __init__(self, schema: dict[str, Any], cls: type[Trie]) -> None:
        r"""Init.

        :param schema:
        :type schema: dict[str, Any]
        :param cls:
        :type cls: type[Trie]
        :rtype: None
        """
        self.validator = self.schema2validator(schema)
        self.cls = cls

    @staticmethod
    def schema2validator(schema: dict[str, Any]) -> Validator:
        r"""Schema2validator.

        :param schema:
        :type schema: dict[str, Any]
        :rtype: Validator
        """
        return validator_for(schema)(schema)

    def get_diagnostics(self, _: str, tree: Tree) -> list[Diagnostic]:
        r"""Get diagnostics.

        :param _:
        :type _: str
        :param tree:
        :type tree: Tree
        :rtype: list[Diagnostic]
        """
        trie = self.cls.from_tree(tree)
        return [
            Diagnostic(
                trie.from_path(error.json_path).range,
                error.message,
                DiagnosticSeverity.Error,
            )
            for error in self.validator.iter_errors(trie.to_json())
        ]


@dataclass(init=False)
class QueryFinder(Finder):
    r"""Queryfinder."""

    def __init__(
        self,
        query: Query,
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param query:
        :type query: Query
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        self.query = query
        super().__init__(message, severity)

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
        tree = self.prepare(uri, tree, reset)
        captures = self.query.captures(tree.root_node)
        return self.captures2unis(captures, uri)

    def captures2unis(
        self, captures: list[tuple[Node, str]], uri: str
    ) -> list[UNI]:
        r"""Captures2unis.

        :param captures:
        :type captures: list[tuple[Node, str]]
        :param uri:
        :type uri: str
        :rtype: list[UNI]
        """
        unis = []
        for capture in captures:
            if uni := self.capture2uni(capture, uri):
                unis += [uni]
        return unis

    def capture2uni(self, capture: tuple[Node, str], uri: str) -> UNI | None:
        r"""Capture2uni.

        :param capture:
        :type capture: tuple[Node, str]
        :param uri:
        :type uri: str
        :rtype: UNI | None
        """
        return UNI(uri, capture[0])


@dataclass(init=False)
class ErrorFinder(QueryFinder):
    r"""Errorfinder."""

    def __init__(
        self,
        language: Language | None = None,
        message: str = "{{uni.get_text()}}: error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ):
        r"""Init.

        :param language:
        :type language: Language | None
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        """
        with open(
            os.path.join(
                os.path.join(
                    os.path.join(os.path.dirname(__file__), "assets"),
                    "queries",
                ),
                "error.scm",
            )
        ) as f:
            text = f.read()
        if language is not None:
            query = language.query(text)
            super().__init__(query, message, severity)
        else:
            Finder.__init__(self, message, severity)
            self.find_all = Finder().find_all

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        node = uni.node
        return node.has_error and not (
            any(child.has_error for child in node.children)
        )


@dataclass(init=False)
class ErrorQueryFinder(ErrorFinder):
    r"""Errorqueryfinder."""

    def __init__(
        self,
        filetype: str,
        message: str = "{{uni.get_text()}}: error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param filetype:
        :type filetype: str
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        from tree_sitter_languages import get_language

        language = get_language(filetype)
        super().__init__(language, message, severity)
