r"""Linter
==========

Support lint/link/diagnose.
"""

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from shlex import split
from types import ModuleType
from typing import Any

import jq
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    DocumentLink,
    Range,
)
from tree_sitter import Language, Node, Query, QueryCursor, Tree

from .node import NodeRange, NodeText, NodeTuples, PackageSearcher


@dataclass
class LinterBase:
    def diagnose(self, tree: Tree, path: str) -> list[Diagnostic]:
        raise NotImplementedError

    def link(self, tree: Tree, path: str) -> list[DocumentLink]:
        raise NotImplementedError


@dataclass
class Linter(LinterBase):
    query: Query

    def __post_init__(self):
        self.cursor = QueryCursor(self.query)

    @staticmethod
    def queries_to_query(
        language: Language, queries: ModuleType, name: str
    ) -> Query:
        paths: list[str] = queries.__path__._path  # ty:ignore[unresolved-attribute]
        query_file = os.path.join(paths[0], name)
        with open(query_file) as f:
            text = f.read()
        query = Query(language, text)
        return query

    def __call__(
        self,
        tree: Tree,
        path: str,
        callback: Callable[[Range, str, str, DiagnosticSeverity], Any],
    ) -> list[Any]:
        raise NotImplementedError

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
    expanduser: bool = True
    expandvars: bool = True

    @classmethod
    def from_queries(
        cls, language: Language, queries: ModuleType, *args, **kwargs
    ) -> "PathLinter":
        query = cls.queries_to_query(language, queries, "highlights.scm")
        return cls(query, *args, **kwargs)

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
                text = NodeText(node)
                if self.expanduser:
                    text = os.path.expanduser(text)
                if self.expandvars:
                    text = os.path.expandvars(text)
                filepath = os.path.join(dirname, text)
                exist = os.path.exists(filepath)
                if callback == self.get_link:
                    if not exist:
                        continue
                    path = filepath
                    message = ""
                else:
                    if exist:
                        continue
                    message = "invalid path " + filepath
                range = NodeRange(node)
                item = callback(range, message, path, DiagnosticSeverity.Error)
                items += [item]
        return items


@dataclass
class PackageLinter(Linter):
    searcher_getter: Callable[[str], PackageSearcher | None]

    @classmethod
    def from_queries(
        cls, language: Language, queries: ModuleType, *args, **kwargs
    ) -> "PackageLinter":
        query = cls.queries_to_query(language, queries, "packages.scm")
        return cls(query, *args, **kwargs)

    def __call__(
        self,
        tree: Tree,
        path: str,
        callback: Callable[[Range, str, str, DiagnosticSeverity], Any],
    ) -> list[Any]:
        searcher = self.searcher_getter(path)
        if searcher is None:
            return []
        captures = self.cursor.captures(tree.root_node)
        items = []
        for label, nodes in captures.items():
            if label != searcher.label:
                continue
            for node in nodes:
                # use label is enough
                # if not searcher(node):
                #     continue
                name = NodeText(node)
                exists = searcher.has_package(name)
                if callback == self.get_link:
                    if not exists:
                        continue
                    path = searcher.get_package_url(name)
                    message = ""
                else:
                    if exists:
                        continue
                    message = "unknown package " + name
                range = NodeRange(node)
                item = callback(
                    range, message, path, DiagnosticSeverity.Warning
                )
                items += [item]
        return items


class Args(dict[str, str]):
    r"""Environment for jq"""

    @staticmethod
    def get_obj_type(scope: str) -> Callable[[str], Any]:
        match scope:
            case "integer":
                obj_type = int
            case "number":
                obj_type = float
            case "string":
                obj_type = str
            case "shlex":

                def obj_type(x):
                    return split(x)[0]

            case boolean:
                _, *falses = boolean.split("-")

                def obj_type(x, falses=falses or ["false"]):
                    return x not in falses

        return obj_type

    def parse_key(
        self,
        key: str,
        lens: dict[str, int],
        instance,
    ) -> tuple[str, Callable[[str], Any]]:
        code = "."
        scopes = key.split(".")
        obj_type = str
        for scope in scopes:
            if scope == "-":
                if code not in lens:
                    lens[code] = self.get_len_by_code(instance, code)
                scope = lens[code]
            elif scope == "--":
                lens[code] = self.get_len_by_code(instance, code)
                scope = lens[code]
            elif scope.startswith("--"):
                obj_type = self.get_obj_type(scope[2:])
                break
            elif scope.startswith("-"):
                scope = self[scope[1:]]
            code += f"[{json.dumps(scope)}]"
        return code, obj_type

    def get_by_code(self, instance, code: str):
        program = jq.compile(code, args=self)
        result = program.input_value(instance).first()
        return result

    def get_len_by_code(self, instance, code: str) -> int:
        result = self.get_by_code(instance, code)
        return len(result) if isinstance(result, list) else 0

    def has_by_code(self, instance, code: str) -> bool:
        result = self.get_by_code(instance, code)
        return result is not None

    def set_by_code(self, result, code: str, obj):
        program = jq.compile(code + f" = {json.dumps(obj)}", args=self)
        result = program.input_value(result).first()
        return result


@dataclass
class SchemaLinter(Linter):
    validator_getter: Callable[[str], Validator | None]
    regex: re.Pattern = field(
        default_factory=lambda: re.compile(r"\('([^']+)' was unexpected\)")
    )

    @classmethod
    def from_queries(
        cls,
        language: Language,
        queries: ModuleType,
        schema_getter: str | Callable[[str], Any],
    ) -> "SchemaLinter":
        query = cls.queries_to_query(language, queries, "schema.scm")

        if isinstance(schema_getter, str):
            with open(schema_getter) as f:
                schema = json.load(f)

            def schema_getter(_: str):
                return schema

        return cls.from_schema(query, schema_getter)

    @classmethod
    def from_schema(
        cls, query: Query, schema_getter: Callable[[str], Any]
    ) -> "SchemaLinter":
        def validator_getter(path: str) -> Validator:
            schema = schema_getter(path)
            return validator_for(schema)(schema)

        return cls(query, validator_getter)

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
        validator = self.validator_getter(path)
        if validator is None:
            return []
        matches = self.cursor.matches(tree.root_node)
        text_instance = self.instantiate(matches, NodeText)
        tuple_instance = self.instantiate(matches, NodeTuples)
        items = []
        for error in validator.iter_errors(text_instance):
            # strip $
            code = error.json_path[1:].replace("'", '"')
            if len(code) == 0 or code[0] != ".":
                code = "." + code
            program = jq.compile(code)
            tup = program.input_value(tuple_instance).first()

            def tuple_to_item(tup, error=error):
                range = NodeRange.from_tuples(tup)
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

    @staticmethod
    def process_settings(
        settings: dict[str, str | None],
    ) -> tuple[dict[str, str], dict[str, str]]:
        args: dict[str, str] = {}
        values: dict[str, str] = {}
        for key, value in settings.items():
            if key.startswith("--") and key != "--":
                args[key[2:]] = value or ""
            else:
                values[key] = value or ""
        return args, values

    def instantiate(
        self,
        matches: list[tuple[int, dict[str, list[Node]]]],
        callback: Callable[[Node], Any],
    ):
        r"""Get a JSON instance for JSON schema validation."""
        instance = {}
        for i, match in matches:
            # build args
            args, values = self.process_settings(
                self.query.pattern_settings(i)
            )
            objs = []
            for key, nodes in match.items():
                for node in nodes:
                    if key.startswith("--") and key != "--":
                        args[key[2:]] = NodeText(node)
                    else:
                        objs += [(key, callback(node))]
            args = Args(**args)

            # keep invariable for each match
            lens: dict[str, int] = {}
            for key, obj in objs:
                code, obj_type = args.parse_key(key, lens, instance)
                if isinstance(obj, str):
                    obj = obj_type(obj)
                instance = args.set_by_code(instance, code, obj)
            for key, obj in values.items():
                code, obj_type = args.parse_key(key, lens, instance)
                if args.has_by_code(instance, code):
                    continue
                obj = obj_type(obj)
                instance = args.set_by_code(instance, code, obj)
        return instance
