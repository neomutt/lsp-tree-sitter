r"""Linter
==========

Support lint/link/diagnose.
"""

import json
import os
import re
from collections.abc import Callable
from contextlib import suppress
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
    DocumentSymbol,
    InlayHint,
)
from tree_sitter import Language, Node, Query, QueryCursor, Tree

from .node import NodeRange, NodeText, NodeTuples, PackageSearcher


@dataclass
class LinterBase:
    r"""Linter base."""

    def diagnose(self, tree: Tree, path: str) -> list[Diagnostic]:
        r"""Get diagnostics.

        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[Diagnostic]
        """
        return []

    def link(self, tree: Tree, path: str) -> list[DocumentLink]:
        r"""Get links.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[DocumentLink]
        """
        return []

    def hint(self, tree: Tree, path: str) -> list[InlayHint]:
        r"""Get inlay hints.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[InlayHint]
        """
        return []

    def symbol(self, tree: Tree, path: str) -> list[DocumentSymbol]:
        r"""Get symbols.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[DocumentSymbol]
        """
        return []


@dataclass
class Linter(LinterBase):
    r"""Linter."""

    query: Query

    def __post_init__(self):
        r"""Post init.

        :param self:
        """
        self.cursor = QueryCursor(self.query)

    @staticmethod
    def queries_to_query(
        language: Language, queries: ModuleType, name: str
    ) -> Query:
        r"""Queries to query.

        :param language:
        :type language: Language
        :param queries:
        :type queries: ModuleType
        :param name:
        :type name: str
        :rtype: Query
        """
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
        cls: type,
    ) -> list[Any]:
        r"""diagnose, link, hint, symbol call it.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :param cls:
        :type cls: type
        :rtype: list[Any]
        """
        raise NotImplementedError

    def diagnose(self, tree: Tree, path: str) -> list[Diagnostic]:
        r"""Get diagnostics.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[Diagnostic]
        """
        return self(tree, path, Diagnostic)

    def link(self, tree: Tree, path: str) -> list[DocumentLink]:
        r"""Get links.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[DocumentLink]
        """
        return self(tree, path, DocumentLink)

    def hint(self, tree: Tree, path: str) -> list[InlayHint]:
        r"""Get inlay hints.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[InlayHint]
        """
        return self(tree, path, InlayHint)

    def symbol(self, tree: Tree, path: str) -> list[DocumentSymbol]:
        r"""Get symbols.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :rtype: list[DocumentSymbol]
        """
        return self(tree, path, DocumentSymbol)


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
        r"""Factory function from queries.

        :param cls:
        :param language:
        :type language: Language
        :param queries:
        :type queries: ModuleType
        :param args:
        :param kwargs:
        :rtype: PathLinter
        """
        query = cls.queries_to_query(language, queries, "highlights.scm")
        return cls(query, *args, **kwargs)

    def __call__(
        self,
        tree: Tree,
        path: str,
        cls: type,
    ) -> list[Any]:
        r"""diagnose, link, hint, symbol call it.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :param cls:
        :type cls: type
        :rtype: list[Any]
        """
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
                range = NodeRange.from_node(node)
                if cls == Diagnostic:
                    if exist:
                        continue
                    item = Diagnostic(
                        range,
                        "invalid path " + filepath,
                        DiagnosticSeverity.Error,
                    )
                elif cls == DocumentLink:
                    if not exist:
                        continue
                    item = DocumentLink(range, filepath)
                else:
                    continue
                items += [item]
        return items


@dataclass
class PackageLinter(Linter):
    r"""Package linter."""

    searcher_getter: Callable[[str], PackageSearcher | None]

    @classmethod
    def from_queries(
        cls, language: Language, queries: ModuleType, *args, **kwargs
    ) -> "PackageLinter":
        r"""Factory function from queries.

        :param cls:
        :param language:
        :type language: Language
        :param queries:
        :type queries: ModuleType
        :param args:
        :param kwargs:
        :rtype: PackageLinter
        """
        query = cls.queries_to_query(language, queries, "packages.scm")
        return cls(query, *args, **kwargs)

    def __call__(
        self,
        tree: Tree,
        path: str,
        cls: type,
    ) -> list[Any]:
        r"""diagnose, link, hint, symbol call it.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :param cls:
        :type cls: type
        :rtype: list[Any]
        """
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
                name = searcher.get_package_name(name)
                exists = searcher.has_package(name)
                range = NodeRange.from_node(node)
                if cls == Diagnostic:
                    if exists:
                        continue
                    item = Diagnostic(
                        range,
                        "unknown package " + name,
                        DiagnosticSeverity.Warning,
                    )
                elif cls == Diagnostic:
                    if not exists:
                        continue
                    item = DocumentLink(range, searcher.get_package_url(name))
                elif cls == InlayHint:
                    if not exists:
                        continue
                    version = searcher.get_package_version(name)
                    if version == "":
                        continue
                    item = InlayHint(range.end, version, padding_left=True)
                else:
                    continue
                items += [item]
        return items


class Args(dict[str, str]):
    r"""Environment for jq"""

    @staticmethod
    def get_obj_type(scope: str) -> Callable[[str], Any]:
        r"""Get obj type.

        :param scope:
        :type scope: str
        :rtype: Callable[[str], Any]
        """
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
        r"""Parse key.

        :param self:
        :param key:
        :type key: str
        :param lens:
        :type lens: dict[str, int]
        :param instance:
        :rtype: tuple[str, Callable[[str], Any]]
        """
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
        r"""Get by code.

        :param self:
        :param instance:
        :param code:
        :type code: str
        """
        program = jq.compile(code, args=self)
        result = program.input_value(instance).first()
        return result

    def get_len_by_code(self, instance, code: str) -> int:
        r"""Get len by code.

        :param self:
        :param instance:
        :param code:
        :type code: str
        :rtype: int
        """
        result = self.get_by_code(instance, code)
        return len(result) if isinstance(result, list) else 0

    def has_by_code(self, instance, code: str) -> bool:
        r"""Has by code.

        :param self:
        :param instance:
        :param code:
        :type code: str
        :rtype: bool
        """
        result = self.get_by_code(instance, code)
        return result is not None

    def set_by_code(self, result, code: str, obj):
        r"""Set by code.

        :param self:
        :param result:
        :param code:
        :type code: str
        :param obj:
        """
        program = jq.compile(code + f" = {json.dumps(obj)}", args=self)
        result = program.input_value(result).first()
        return result


@dataclass
class SchemaLinter(Linter):
    r"""Schema linter."""

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
        r"""Factory function from queries.

        :param cls:
        :param language:
        :type language: Language
        :param queries:
        :type queries: ModuleType
        :param schema_getter:
        :type schema_getter: str | Callable[[str], Any]
        :rtype: SchemaLinter
        """
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
        r"""From schema.

        :param cls:
        :param query:
        :type query: Query
        :param schema_getter:
        :type schema_getter: Callable[[str], Any]
        :rtype: SchemaLinter
        """

        def validator_getter(path: str) -> Validator | None:
            schema = schema_getter(path)
            return validator_for(schema)(schema) if schema else None

        return cls(query, validator_getter)

    @staticmethod
    def tuple_is_range(tup) -> bool:
        r"""Judge if the tuple is a range.

        :param tup:
        :rtype: bool
        """
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
        cls: type,
    ) -> list[Any]:
        r"""diagnose, link, hint, symbol call it.

        :param self:
        :param tree:
        :type tree: Tree
        :param path:
        :type path: str
        :param cls:
        :type cls: type
        :rtype: list[Any]
        """
        if cls != Diagnostic:
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
                item = Diagnostic(
                    range, error.message, DiagnosticSeverity.Error
                )
                return item

            if self.tuple_is_range(tup):
                items += [tuple_to_item(tup)]
            elif isinstance(tup, list) and all(
                self.tuple_is_range(child) for child in tup
            ):
                # https://github.com/python-jsonschema/jsonschema/issues/1363
                if error.message.endswith(" has non-unique elements"):
                    texts: list[str] = program.input_value(
                        text_instance
                    ).first()
                    for i in self.get_duplications(texts):
                        items += [tuple_to_item(tup[i])]
                else:
                    for child in tup:
                        items += [tuple_to_item(child)]
            elif isinstance(tup, dict):
                # https://github.com/python-jsonschema/jsonschema/issues/119
                if error.message.endswith(" was unexpected"):
                    for key in self.regex.findall(error.message):
                        items += [tuple_to_item(tup[key])]
                elif error.message.endswith(" is a required property"):
                    items += [tuple_to_item(tup[0])]
                else:
                    for child in tup.values():
                        items += [tuple_to_item(child)]
            else:
                items += [tuple_to_item([[0, 0], [0, 0]])]
        return items

    @staticmethod
    def get_duplications(arr: list) -> list[int]:
        r"""Get duplications.

        :param arr:
        :type arr: list
        :rtype: list[int]
        """
        seen = {}
        duplicates = set()

        for i, val in enumerate(arr):
            if val in seen:
                duplicates.add(val)
            else:
                seen[val] = i

        return [i for i, val in enumerate(arr) if val in duplicates]

    @staticmethod
    def process_settings(
        settings: dict[str, str | None],
    ) -> tuple[dict[str, str], dict[str, str]]:
        r"""Process settings.

        :param settings:
        :type settings: dict[str, str | None]
        :rtype: tuple[dict[str, str], dict[str, str]]
        """
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
        r"""Get a JSON instance for JSON schema validation.

        :param self:
        :param matches:
        :type matches: list[tuple[int, dict[str, list[Node]]]]
        :param callback:
        :type callback: Callable[[Node], Any]
        """
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
                    with suppress(ValueError):
                        obj = obj_type(obj)
                instance = args.set_by_code(instance, code, obj)
            for key, obj in values.items():
                code, obj_type = args.parse_key(key, lens, instance)
                if args.has_by_code(instance, code):
                    continue
                obj = obj_type(obj)
                instance = args.set_by_code(instance, code, obj)
        return instance
