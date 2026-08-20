r"""Server
==========
"""

import sys
from typing import TYPE_CHECKING

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_LINK,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_INLAY_HINT,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DocumentLink,
    DocumentLinkParams,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    InlayHint,
    InlayHintParams,
    MarkupContent,
    MarkupKind,
    PublishDiagnosticsParams,
    TextDocumentContentChangePartial,
    TextDocumentPositionParams,
)
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path
from pygls.workspace import ServerTextPosition, TextDocument
from tree_sitter import Parser, Tree

from .completer import Completer
from .linter import Linter, SchemaLinter
from .node import NodeText
from .utils import pprint

if TYPE_CHECKING:
    from argparse import Namespace


class TreeSitterTextDocument(TextDocument):
    r"""TextDocument for tree sitter."""

    def position_to_byte_offset(
        self, position: ServerTextPosition
    ) -> tuple[int, int]:
        r"""Convert a (line, col) position to a byte offset and byte column.
        Returns ``(byte_offset, byte_col)`` where ``byte_col`` is the number
        of UTF-8 bytes from the start of ``line`` to ``col``.

        :param self:
        :param position: ``line`` and ``col`` are zero-based and given in
            UTF-32 code points (Python characters), as returned by pygls'
            ``PositionCodec``.
        :type position: ServerTextPosition
        :rtype: tuple[int, int]
        """
        # index out of length
        lines = self.source.encode().split(b"\n")
        line_start = sum(
            len(lines[i]) + 1 for i in range(min(position.line, len(lines)))
        )
        if position.line >= len(lines):
            return line_start, 0
        line_str = lines[position.line].decode()
        byte_col = len(
            line_str[: min(position.character, len(line_str))].encode()
        )
        return line_start + byte_col, byte_col

    def compute_tree_edit(
        self, change: TextDocumentContentChangePartial
    ) -> dict:
        r"""Compute ``Tree.edit()`` kwargs from a LSP incremental content
        change.

        :param self:
        :param change:
        :type change: TextDocumentContentChangePartial
        :rtype: dict
        """
        lines = self.source.splitlines(True)
        range = self.position_codec.range_from_client_units(
            lines, change.range
        )

        start_byte, start_bcol = self.position_to_byte_offset(range.start)
        old_end_byte, old_end_bcol = self.position_to_byte_offset(range.end)

        bytes_len = len(change.text.encode())
        new_text_lines = change.text.split("\n")

        new_end_byte = start_byte + bytes_len
        new_end_line = range.start.line + len(new_text_lines) - 1
        if len(new_text_lines) == 1:
            new_end_bcol = start_bcol + bytes_len
        else:
            new_end_bcol = len(new_text_lines[-1].encode())

        return dict(
            start_byte=start_byte,
            old_end_byte=old_end_byte,
            new_end_byte=new_end_byte,
            start_point=(range.start.line, start_bcol),
            old_end_point=(range.end.line, old_end_bcol),
            new_end_point=(new_end_line, new_end_bcol),
        )


class TreeSitterLanguageServer(LanguageServer):
    r"""Languageserver based tree sitter."""

    @staticmethod
    def get_name(parser: Parser) -> str:
        r"""Get name.

        :param parser:
        :type parser: Parser
        :rtype: str
        """
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
        r"""Init.

        :param self:
        :param parser:
        :type parser: Parser
        :param linters:
        :type linters: tuple[Linter, ...]
        :param completers:
        :type completers: tuple[Completer, ...]
        :param args:
        :param kwargs:
        :rtype: None
        """
        name = self.get_name(parser)
        super().__init__(name, *args, **kwargs)
        self.parser = parser
        self.linters = linters
        self.completers = completers
        self.trees: dict[str, Tree] = {}

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        def _(params: DidOpenTextDocumentParams) -> None:
            uri = params.text_document.uri
            source = params.text_document.text.encode()
            self.trees[uri] = self.parser.parse(source)
            self.diagnose(params)

        @self.feature(TEXT_DOCUMENT_DID_CLOSE)
        def _(params: DidCloseTextDocumentParams) -> None:
            uri = params.text_document.uri
            if uri in self.trees:
                del self.trees[uri]

        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def _(params: DidChangeTextDocumentParams) -> None:
            if len(params.content_changes) == 0:
                return
            uri = params.text_document.uri
            tree = self.trees.get(uri)
            if tree is None:
                doc = self.workspace.get_text_document(uri)
            else:
                doc = TreeSitterTextDocument(uri, NodeText(tree.root_node))

                for change in params.content_changes:
                    if not isinstance(
                        change, TextDocumentContentChangePartial
                    ):
                        tree = None
                        doc = TextDocument(uri, change.text)
                        break
                    edit = doc.compute_tree_edit(change)
                    tree.edit(**edit)
                    doc.apply_change(change)
            source = doc.source.encode()

            # TypeError: parse() argument 2 must be tree_sitter.Tree, not None
            tree = (
                self.parser.parse(source, old_tree=tree)
                if tree
                else self.parser.parse(source)
            )
            self.trees[uri] = tree
            self.diagnose(params)

        @self.feature(TEXT_DOCUMENT_DOCUMENT_LINK)
        def _(params: DocumentLinkParams) -> list[DocumentLink]:
            return self.link(params)

        @self.feature(TEXT_DOCUMENT_INLAY_HINT)
        def _(params: InlayHintParams) -> list[InlayHint]:
            return self.hint(params)

        @self.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
        def _(params: DocumentSymbolParams) -> list[DocumentSymbol]:
            return self.symbol(params)

        @self.feature(TEXT_DOCUMENT_HOVER)
        def _(params: TextDocumentPositionParams) -> Hover | None:
            return self.hover(params)

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            return self.complete(params)

    def diagnose(
        self,
        params: DidOpenTextDocumentParams | DidChangeTextDocumentParams,
    ) -> None:
        r"""Publish diagnostics.

        :param self:
        :param params:
        :type params: DidOpenTextDocumentParams | DidChangeTextDocumentParams
        :rtype: None
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        diagnostics = []
        for linter in self.linters:
            diagnostics += linter.diagnose(tree, to_fs_path(uri) or "")
        self.text_document_publish_diagnostics(
            PublishDiagnosticsParams(uri, diagnostics)
        )

    def link(self, params: DocumentLinkParams) -> list[DocumentLink]:
        r"""Get links.

        :param self:
        :param params:
        :type params: DocumentLinkParams
        :rtype: list[DocumentLink]
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        links = []
        for linter in self.linters:
            links += linter.link(tree, to_fs_path(uri) or "")
        return links

    def hint(self, params: InlayHintParams) -> list[InlayHint]:
        r"""Get inlay hints.

        :param self:
        :param params:
        :type params: InlayHintParams
        :rtype: list[InlayHint]
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        hints = []
        for linter in self.linters:
            hints += linter.hint(tree, to_fs_path(uri) or "")
        return hints

    def symbol(self, params: DocumentSymbolParams) -> list[DocumentSymbol]:
        r"""Get symbols.

        :param self:
        :param params:
        :type params: DocumentSymbolParams
        :rtype: list[DocumentSymbol]
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        symbols = []
        for linter in self.linters:
            symbols += linter.symbol(tree, to_fs_path(uri) or "")
        return symbols

    def hover(self, params: TextDocumentPositionParams) -> Hover | None:
        r"""Get a hover.

        :param self:
        :param params:
        :type params: TextDocumentPositionParams
        :rtype: Hover | None
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        for completer in self.completers:
            result = completer.hover(
                tree, params.position, to_fs_path(uri) or ""
            )
            if result:
                return result

    def complete(self, params: CompletionParams) -> CompletionList:
        r"""Get a completion list.

        :param self:
        :param params:
        :type params: CompletionParams
        :rtype: CompletionList
        """
        uri = params.text_document.uri
        tree = self.trees[uri]
        items = []
        for completer in self.completers:
            items += completer.complete(
                tree, params.position, to_fs_path(uri) or ""
            ).items
        return CompletionList(items == [], items)

    def lookup(
        self,
        *texts: str,
        kind: str = "option",
        path: str = "",
        complete: bool = False,
    ) -> dict[str, list[MarkupContent]]:
        r"""Look up documentation.

        :param self:
        :param texts:
        :type texts: str
        :param kind:
        :type kind: str
        :param path:
        :type path: str
        :param complete:
        :type complete: bool
        :rtype: dict[str, list[MarkupContent]]
        """
        contents: dict[str, list[MarkupContent]] = {}
        for text in texts:
            contents[text] = []
            for completer in self.completers:
                if complete:
                    items = completer.lookup_complete(kind, text, path)
                    for item in items:
                        if item.documentation is None:
                            continue
                        if isinstance(item.documentation, str):
                            contents[text] += [
                                MarkupContent(
                                    MarkupKind.PlainText, item.documentation
                                )
                            ]
                        else:
                            contents[text] += [item.documentation]
                else:
                    content = completer.lookup_help(kind, text, path)
                    if content:
                        contents[text] += [content]
        return contents

    def lint(self, *files: str) -> dict[str, list[Diagnostic]]:
        r"""Lint.

        :param self:
        :param files:
        :type files: str
        :rtype: dict[str, list[Diagnostic]]
        """
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
        r"""Instantiate files to JSON data.

        :param self:
        :param files:
        :type files: str
        :rtype: dict[str, list[dict]]
        """
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
                instances[file] += [linter.instantiate(matches, NodeText)]
        return instances

    def run(self, args: "Namespace") -> None:
        r"""Run.

        :param self:
        :param args:
        :type args: Namespace
        :rtype: None
        """
        match args.color:
            case "always":
                color = True
            case "never":
                color = False
            case _:
                color = sys.stdout.isatty()
        for contents in self.lookup(
            *args.lookup,
            kind=args.type,
            path=args.path,
            complete=args.complete,
        ).values():
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

        if args.tcp:
            self.start_tcp(args.host, args.port)
        elif args.ws:
            self.start_ws(args.host, args.port)
        if not (args.lookup or args.check or args.convert):
            self.start_io()
