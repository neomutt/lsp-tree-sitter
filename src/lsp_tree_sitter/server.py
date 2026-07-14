r"""Server
==========
"""

import sys
from typing import TYPE_CHECKING

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_LINK,
    TEXT_DOCUMENT_HOVER,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DocumentLink,
    DocumentLinkParams,
    Hover,
    MarkupContent,
    PublishDiagnosticsParams,
    TextDocumentPositionParams,
)
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path
from tree_sitter import Parser, Tree

from .completer import Completer
from .linter import Linter, SchemaLinter
from .utils import pprint

if TYPE_CHECKING:
    from argparse import Namespace


class TreeSitterLanguageServer(LanguageServer):
    @staticmethod
    def get_name(parser: Parser) -> str:
        language = parser.language
        name = language.name or "" if language else ""
        return name

    def __init__(
        self,
        parser: Parser,
        linters: tuple[Linter, ...],
        completers: tuple[Completer, ...],
        *args,
        **kwargs,
    ) -> None:
        name = self.get_name(parser)
        super().__init__(name, *args, **kwargs)
        self.parser = parser
        self.linters = linters
        self.completers = completers
        self.trees: dict[str, Tree] = {}

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def _(params: DidChangeTextDocumentParams) -> None:
            doc = self.workspace.get_text_document(params.text_document.uri)
            source = doc.source.encode()
            # TODO: incremental parsing
            tree = self.parser.parse(source)
            self.trees[doc.uri] = tree
            self.diagnose(params)

        @self.feature(TEXT_DOCUMENT_DOCUMENT_LINK)
        def _(params: DocumentLinkParams) -> list[DocumentLink]:
            return self.link(params)

        @self.feature(TEXT_DOCUMENT_HOVER)
        def _(params: TextDocumentPositionParams) -> Hover | None:
            return self.hover(params)

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            return self.complete(params)

    def diagnose(self, params: DidChangeTextDocumentParams) -> None:
        doc = self.workspace.get_text_document(params.text_document.uri)
        tree = self.trees[doc.uri]
        diagnostics = []
        for linter in self.linters:
            diagnostics += linter.diagnose(tree, to_fs_path(doc.uri) or "")
        self.text_document_publish_diagnostics(
            PublishDiagnosticsParams(doc.uri, diagnostics)
        )

    def link(self, params: DocumentLinkParams) -> list[DocumentLink]:
        doc = self.workspace.get_text_document(params.text_document.uri)
        tree = self.trees[doc.uri]
        links = []
        for linter in self.linters:
            links += linter.link(tree, to_fs_path(doc.uri) or "")
        return links

    def hover(self, params: TextDocumentPositionParams) -> Hover | None:
        doc = self.workspace.get_text_document(params.text_document.uri)
        tree = self.trees[doc.uri]
        for completer in self.completers:
            result = completer.hover(
                tree, params.position, to_fs_path(doc.uri) or ""
            )
            if result:
                return result

    def complete(self, params: CompletionParams) -> CompletionList:
        doc = self.workspace.get_text_document(params.text_document.uri)
        tree = self.trees[doc.uri]
        items = []
        for completer in self.completers:
            items += completer.complete(
                tree, params.position, to_fs_path(doc.uri) or ""
            ).items
        return CompletionList(items == [], items)

    def lookup(self, kind: str, *texts: str) -> dict[str, list[MarkupContent]]:
        contents: dict[str, list[MarkupContent]] = {}
        for text in texts:
            contents[text] = []
            for completer in self.completers:
                content = completer.lookup_help(kind, text)
                if content:
                    contents[text] += [content]
        return contents

    def lint(self, *files: str) -> dict[str, list[Diagnostic]]:
        diagnostics: dict[str, list[Diagnostic]] = {}
        for file in files:
            diagnostics[file] = []
            with open(file, "rb") as f:
                source = f.read()
            tree = self.parser.parse(source)
            for linter in self.linters:
                diagnostics[file] += linter.diagnose(tree, file)
        return diagnostics

    def instantiate(self, *files: str) -> dict[str, list[dict]]:
        instances: dict[str, list[dict]] = {}
        for file in files:
            instances[file] = []
            with open(file, "rb") as f:
                source = f.read()
            tree = self.parser.parse(source)
            for linter in self.linters:
                if not isinstance(linter, SchemaLinter):
                    continue
                matches = linter.cursor.matches(tree.root_node)
                instances[file] += [
                    linter.instantiate(matches, linter.text_callback)
                ]
        return instances

    def run(self, args: "Namespace") -> None:
        if not (args.lookup or args.check or args.convert):
            self.start_io()
            return
        match args.color:
            case "always":
                color = True
            case "never":
                color = False
            case _:
                color = sys.stdout.isatty()
        for contents in self.lookup(args.type, *args.lookup).values():
            for content in contents:
                pprint(content.value, content.kind, color)
        for file, diagnostics in self.lint(*args.check).items():
            for diagnostic in diagnostics:
                message = args.message_format.format(
                    file=file,
                    range=diagnostic.range,
                    severity=(
                        diagnostic.severity or DiagnosticSeverity.Error
                    ).name.lower(),
                    message=diagnostic.message,
                )
                # TODO: use pprint()
                print(message)
        for instances in self.instantiate(*args.convert).values():
            for instance in instances:
                pprint(instance, args.output_format, color, indent=args.indent)
