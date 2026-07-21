r"""Completer
=============
"""

import json
import os
import re
from collections.abc import Callable, Iterable
from contextlib import suppress
from dataclasses import dataclass, field
from glob import glob
from typing import Any

import jq
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    Hover,
    MarkupContent,
    MarkupKind,
    Position,
)
from tree_sitter import Node, Point, Tree

from .linter import Linter


@dataclass
class Completer:
    def complete(
        self, tree: Tree, position: Position, path: str
    ) -> CompletionList:
        point = Point(position.line, position.character - 1)
        node = tree.root_node.descendant_for_point_range(point, point)
        args = self.args_callback(node, point)
        args["complete"] = True
        results = self(args, path, node)
        items = []
        for result in results:
            item = CompletionItem(
                result["label"],
                insert_text=result["insert_text"],
                kind=result["kind"],
                documentation=MarkupContent(**result["documentation"])
                if result.get("documentation", None)
                else None,
            )
            items += [item]
        return CompletionList(items == [], items)

    def hover(self, tree: Tree, position: Position, path: str) -> Hover | None:
        point = Point(position.line, position.character)
        node = tree.root_node.descendant_for_point_range(point, point)
        args = self.args_callback(node, point)
        results = self(args, path, node)
        if results == [] or results[0]["documentation"] is None:
            return None
        content = MarkupContent(**results[0]["documentation"])
        return Hover(content, Linter.tuple_to_range(args["range"]))

    def lookup_help(
        self,
        type: str,
        text: str = "",
        path: str = "",
        **kwargs,
    ) -> MarkupContent | None:
        args = self.args_callback(None, Point(-1, -1))
        args["type"] = type
        args["text"] = text
        args.update(kwargs)
        results = self(args, path)
        if results == [] or results[0]["documentation"] is None:
            return None
        return MarkupContent(**results[0]["documentation"])

    def lookup_complete(
        self,
        type: str,
        text: str = "",
        path: str = "",
        **kwargs,
    ) -> list[CompletionItem]:
        args = self.args_callback(None, Point(-1, -1))
        args["type"] = type
        args["text"] = text
        args["complete"] = True
        args.update(kwargs)
        results = self(args, path)
        items = []
        for result in results:
            item = CompletionItem(
                result["label"],
                insert_text=result["insert_text"],
                kind=result["kind"],
                documentation=MarkupContent(**result["documentation"])
                if result.get("documentation", None)
                else None,
            )
            items += [item]
        return items

    @staticmethod
    def args_callback(node: Node | None, point: Point) -> dict[str, Any]:
        return {
            "type": node.type if node else "",
            "text": Linter.text_callback(node) if node else "",
            "cursor": tuple(point),
            "range": Linter.tuple_callback(node)
            if node
            else ((-1, -1), (-1, -1)),
            "complete": False,
            "enums": {
                "CompletionItemKind": {
                    member.name: member.value
                    for member in CompletionItemKind.__members__.values()
                },
                "MarkupKind": {
                    member.name: member.value
                    for member in MarkupKind.__members__.values()
                },
            },
        }

    def __call__(
        self, args: dict[str, Any], path: str, node: Node | None = None
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


@dataclass
class PathCompleter(Completer):
    kind: str = "path"
    filetypes: dict[str, str] = field(default_factory=lambda: {"*": "text"})
    regex: re.Pattern = field(
        default_factory=lambda: re.compile(r"^(`+)", re.MULTILINE)
    )

    def __call__(
        self, args: dict[str, Any], path: str, node: Node | None = None
    ) -> list[dict[str, Any]]:
        if args["type"] != self.kind:
            return []
        root_dir = os.path.dirname(path)
        results = []
        for expr, filetype in self.filetypes.items():
            for filename in glob(expr, root_dir=root_dir, recursive=True):
                if not (
                    filename.startswith(args["text"])
                    if args["complete"]
                    else filename == args["text"]
                ):
                    continue
                filepath = os.path.join(root_dir, filename)
                if os.path.isdir(filepath):
                    filename += os.path.sep
                    kind = CompletionItemKind.Folder
                    documentation = {
                        "kind": MarkupKind.PlainText,
                        "value": "\n".join(os.listdir(filepath)),
                    }
                else:
                    kind = CompletionItemKind.File
                    with open(filepath) as f:
                        text = f.read()
                    prefix = "`" + "`" * max(
                        len(prefix)
                        for prefix in self.regex.findall(text) + ["``"]
                    )
                    documentation = {
                        "kind": MarkupKind.Markdown,
                        "value": f"""
{prefix}{filetype}
{text}
{prefix}""",
                    }
                results += [
                    {
                        "label": filename,
                        "insert_text": filename,
                        "documentation": documentation,
                        "kind": kind,
                    }
                ]
        return results


@dataclass
class SchemaCompleter(Completer):
    code: str
    schema_getter: Callable[[str], dict]

    @classmethod
    def from_files(
        cls,
        code_file: str,
        schema_getter: str | Callable[[str], Any],
        *args,
        **kwargs,
    ) -> "SchemaCompleter":
        with open(code_file) as f:
            code = f.read()
        if isinstance(schema_getter, str):
            with open(schema_getter) as f:
                schema = json.load(f)

            def schema_getter(_: str):
                return schema

        return cls(code, schema_getter, *args, **kwargs)

    @staticmethod
    def query(
        code: str, args: dict[str, Any], schema: dict
    ) -> list[dict[str, Any]]:
        program = jq.compile(code, args=args)
        output = program.input_value(schema)
        results = []
        if args["complete"]:
            results = output.all()
        else:
            with suppress(StopIteration):
                results += [output.first()]
        return results

    def __call__(
        self, args: dict[str, Any], path: str, node: Node | None = None
    ) -> list[dict[str, Any]]:
        schema = self.schema_getter(path)
        return self.query(self.code, args, schema)


@dataclass
class ValueCompleter(SchemaCompleter):
    r"""For ``set option value``."""

    selectors: tuple[str, ...] = ("-",)
    regex: re.Pattern = field(
        default_factory=lambda: re.compile(r"([-+^]|\d+)")
    )

    @staticmethod
    def parse_selector(
        selector: str, node: Node | None, regex: re.Pattern
    ) -> Node | None:
        for op in regex.findall(selector):
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

    def args_callback(self, node: Node | None, point: Point) -> dict[str, Any]:
        args = super().args_callback(node, point)
        args["texts"] = []
        for selector in self.selectors:
            node = self.parse_selector(selector, node, self.regex)
            args["texts"] += [Linter.text_callback(node) if node else ""]
        return args


@dataclass
class PackageSearcher:
    texts: tuple[str, ...] = ()
    kind: str = "variable_name"
    selector: str = "^-"

    def __call__(self, node: Node | None) -> bool:
        node = ValueCompleter.parse_selector(
            self.selector, node, ValueCompleter.regex
        )
        return not (
            node is None
            or node.type != self.kind
            or Linter.text_callback(node) not in self.texts
        )

    def get_package_document(self, name: str) -> str | None:
        raise NotImplementedError

    def get_package_names(self, name: str) -> dict[str, str]:
        raise NotImplementedError


@dataclass
class PackageCompleter(Completer):
    """Complete package names."""

    searcher_getter: Callable[[str], PackageSearcher | None]

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

    def __call__(
        self, args: dict[str, Any], path: str, node: Node | None = None
    ) -> list[dict[str, Any]]:
        searcher = self.searcher_getter(path)
        if searcher is None:
            return []

        if not searcher(node):
            return []
        results = []
        name: str = args["text"].strip()
        if args["complete"]:
            for package_name, document in searcher.get_package_names(
                name
            ).items():
                results += [
                    {
                        "label": package_name,
                        "insert_text": package_name,
                        "kind": CompletionItemKind.Variable,
                        "documentation": {
                            "kind": MarkupKind.Markdown,
                            "value": document,
                        },
                    }
                ]
        else:
            document = searcher.get_package_document(name)
            if document:
                results += [
                    {
                        "label": args["text"],
                        "insert_text": args["text"],
                        "kind": CompletionItemKind.Variable,
                        "documentation": {
                            "kind": MarkupKind.Markdown,
                            "value": document,
                        },
                    }
                ]
        return results
