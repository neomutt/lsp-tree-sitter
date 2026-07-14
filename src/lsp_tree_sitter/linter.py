r"""Linter
==========

Support lint/link/diagnose.
"""

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any

import jq
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    DocumentLink,
    Position,
    Range,
)
from tree_sitter import Language, Node, Query, QueryCursor, Tree


@dataclass
class Linter:
    query: Query

    def __post_init__(self):
        self.cursor = QueryCursor(self.query)

    def __call__(
        self,
        tree: Tree,
        path: str,
        callback: Callable[[Range, str, str, DiagnosticSeverity], Any],
    ) -> list[Any]:
        raise NotImplementedError

    @staticmethod
    def text_callback(node: Node) -> str:
        return node.text.decode() if node.text else ""

    @staticmethod
    def tuple_callback(node: Node) -> tuple[tuple[int, int], tuple[int, int]]:
        return tuple(node.start_point), tuple(node.end_point)

    @staticmethod
    def tuple_to_range(tup: tuple[tuple[int, int], tuple[int, int]]) -> Range:
        return Range(Position(*tup[0]), Position(*tup[1]))

    def range_callback(self, node: Node) -> Range:
        return self.tuple_to_range(self.tuple_callback(node))

    @staticmethod
    def get_diagnose(
        range: Range,
        message: str,
        path: str,
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> Diagnostic:
        return Diagnostic(range, message, severity)

    def diagnose(self, tree: Tree, path: str) -> list[Diagnostic]:
        return self(tree, path, self.get_diagnose)

    @staticmethod
    def get_link(
        range: Range,
        message: str,
        path: str,
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> DocumentLink:
        return DocumentLink(range, path, message if message else None)

    def link(self, tree: Tree, path: str) -> list[DocumentLink]:
        return self(tree, path, self.get_link)


@dataclass
class PathLinter(Linter):
    r"""Diagnose incorrect path and link correct path"""

    label: str = "string.special.path"

    @classmethod
    def from_queries(
        cls, language: Language, queries: ModuleType
    ) -> "PathLinter":
        paths: list[str] = queries.__path__._path  # ty:ignore[unresolved-attribute]
        query_file = os.path.join(paths[0], "highlights.scm")
        return cls.from_files(language, query_file)

    @classmethod
    def from_files(cls, language: Language, query_file: str) -> "PathLinter":
        with open(query_file) as f:
            text = f.read()
        query = Query(language, text)
        return cls(query)

    def __call__(
        self,
        tree: Tree,
        path: str,
        callback: Callable[[Range, str, str, DiagnosticSeverity], Any],
    ) -> list[Any]:
        captures = self.cursor.captures(tree.root_node)
        items = []
        dirname = os.path.dirname(path)
        for label, nodes in captures.items():
            if label != self.label:
                continue
            for node in nodes:
                range = self.range_callback(node)
                text = self.text_callback(node)
                filepath = os.path.join(dirname, text)
                exist = os.path.exists(filepath)
                if exist if callback != self.get_link else not exist:
                    continue
                if callback == self.get_link:
                    path = filepath
                    message = ""
                else:
                    message = "invalid path " + filepath
                item = callback(range, message, path, DiagnosticSeverity.Error)
                items += [item]
        return items


@dataclass
class SchemaLinter(Linter):
    validator: Validator
    regex: re.Pattern = field(
        default_factory=lambda: re.compile(r"\('([^']+)' was unexpected\)")
    )

    @classmethod
    def from_queries(
        cls, language: Language, queries: ModuleType, schema_file: str
    ) -> "SchemaLinter":
        paths: list[str] = queries.__path__._path  # ty:ignore[unresolved-attribute]
        query_file = os.path.join(paths[0], "schema.scm")
        return cls.from_files(language, query_file, schema_file)

    @classmethod
    def from_files(
        cls, language: Language, query_file: str, schema_file: str
    ) -> "SchemaLinter":
        with open(query_file) as f:
            text = f.read()
        query = Query(language, text)
        with open(schema_file) as f:
            schema = json.load(f)
        return cls.from_schema(query, schema)

    @classmethod
    def from_schema(cls, query: Query, schema: dict) -> "SchemaLinter":
        return cls(query, validator_for(schema)(schema))

    @staticmethod
    def tuple_is_range(tup) -> bool:
        return (
            isinstance(tup, list)
            and len(tup) == 2
            and all(
                isinstance(child, list) and len(child) == 2 for child in tup
            )
            and all(
                isinstance(grandchild, int)
                for child in tup
                for grandchild in child
            )
        )

    def __call__(
        self,
        tree: Tree,
        path: str,
        callback: Callable[[Range, str, str, DiagnosticSeverity], Any],
    ) -> list[Any]:
        if callback == self.get_link:
            return []
        matches = self.cursor.matches(tree.root_node)
        text_instance = self.instantiate(matches, self.text_callback)
        tuple_instance = self.instantiate(matches, self.tuple_callback)
        items = []
        for error in self.validator.iter_errors(text_instance):
            # strip $
            code = error.json_path[1:].replace("'", '"')
            program = jq.compile(code)
            tup = program.input_value(tuple_instance).first()

            def tuple_to_item(tup, error=error):
                range = self.tuple_to_range(tup)
                item = callback(
                    range, error.message, path, DiagnosticSeverity.Error
                )
                return item

            if self.tuple_is_range(tup):
                items += [tuple_to_item(tup)]
            elif isinstance(tup, list) and all(
                self.tuple_is_range(child) for child in tup
            ):
                for child in tup:
                    items += [tuple_to_item(child)]
            elif isinstance(tup, dict):
                for key in self.regex.findall(error.message):
                    items += [tuple_to_item(tup[key])]
            else:
                items += [tuple_to_item([[0, 0], [0, 0]])]
        return items

    def get_args(
        self, id: int, match: dict[str, list[Node]]
    ) -> dict[str, str]:
        r"""Get args for jq --args"""
        args: dict[str, str] = self.query.pattern_settings(id)  # ty:ignore[invalid-assignment]
        for key, nodes in match.items():
            if key.startswith("--"):
                node = nodes[0]
                args[key[2:]] = self.text_callback(node)
        return args

    def instantiate(
        self,
        matches: list[tuple[int, dict[str, list[Node]]]],
        callback: Callable[[Node], Any],
    ):
        instance = {}
        for i, match in matches:
            args = self.get_args(i, match)
            lengths = {}
            for key, nodes in match.items():
                if key.startswith("--"):
                    continue
                node = nodes[0]
                code = "."
                scopes = key.split(".")
                obj_type = str
                for scope in scopes:
                    if scope == "-":
                        if code not in lengths:
                            program = jq.compile(code, args=args)
                            _instance = program.input_value(instance).first()
                            lengths[code] = (
                                len(_instance)
                                if isinstance(_instance, list)
                                else 0
                            )
                        scope = lengths[code]
                    elif scope.startswith("--"):
                        match scope[2:]:
                            case "integer":
                                obj_type = int
                            case "number":
                                obj_type = float
                            case "string":
                                obj_type = str
                            case boolean:
                                _, *falses = boolean.split("-")

                                def obj_type(x, falses=falses or ["false"]):
                                    return x not in falses

                        break
                    elif scope.startswith("-"):
                        scope = args[scope[1:]]
                    code += f"[{json.dumps(scope)}]"
                obj = callback(node)
                if isinstance(obj, str):
                    obj = obj_type(obj)
                code += f" = {json.dumps(obj)}"
                program = jq.compile(code, args=args)
                instance = program.input_value(instance).first()
        return instance
