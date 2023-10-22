r"""Server
==========
"""
import re
from typing import Any

from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_HOVER,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    Hover,
    InitializeParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentPositionParams,
)
from pygls.server import LanguageServer

from .documents import get_document, get_filetype, get_packages
from .parser import parse
from .tree_sitter_lsp.diagnose import get_diagnostics
from .tree_sitter_lsp.finders import PositionFinder
from .tree_sitter_lsp.format import get_text_edits
from .utils import DIAGNOSTICS_FINDERS, namcap


class PKGBUILDLanguageServer(LanguageServer):
    r"""PKGBUILD language server."""

    def __init__(self, *args: Any) -> None:
        r"""Init.

        :param args:
        :type args: Any
        :rtype: None
        """
        super().__init__(*args)
        self.document = {}
        self.packages = {}
        self.trees = {}

        @self.feature(INITIALIZE)
        def initialize(params: InitializeParams) -> None:
            r"""Initialize.

            :param params:
            :type params: InitializeParams
            :rtype: None
            """
            opts = params.initialization_options
            method = getattr(opts, "method", "builtin")
            self.document = get_document(method)  # type: ignore
            self.packages = get_packages()

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams) -> None:
            r"""Did change.

            :param params:
            :type params: DidChangeTextDocumentParams
            :rtype: None
            """
            if get_filetype(params.text_document.uri) == "":
                return None
            document = self.workspace.get_document(params.text_document.uri)
            diagnostics = []
            if document.path is not None:
                diagnostics += namcap(document.path, document.source)
            self.trees[document.uri] = parse(document.source.encode())
            diagnostics = get_diagnostics(
                DIAGNOSTICS_FINDERS,
                document.uri,
                self.trees[document.uri],
            )
            self.publish_diagnostics(params.text_document.uri, diagnostics)

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: TextDocumentPositionParams) -> Hover | None:
            r"""Hover.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: Hover | None
            """
            filetype = get_filetype(params.text_document.uri)
            if filetype == "":
                return None
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(params.position).find(
                document.uri, self.trees[document.uri]
            )
            if uni is None:
                return None
            text = uni.get_text()
            _range = uni.get_range()
            parent = uni.node.parent
            if parent is None:
                return None
            if parent.type == "array":
                result = self.packages.get(text)
                if result is None:
                    return None
                return Hover(
                    MarkupContent(MarkupKind.Markdown, result), _range
                )
            # PKGBUILD contains package_XXX
            if filetype == "PKGBUILD":
                text = text.split("_")[0]
            type_ = ""
            if uni.node.type == "variable_name":
                type_ = "Variable"
            if uni.node.type == "word" and parent.type in {
                "function_definition",
                "command_name",
            }:
                type_ = "Function"
                text += "()"
            if type_ == "":
                return None
            _type, result, _filetype = self.document.get(text, ["", "", ""])
            if _type == "Field":
                _type = "Variable"
            if result == "" or _filetype != filetype or type_ != _type:
                return None
            return Hover(MarkupContent(MarkupKind.Markdown, result), _range)

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            r"""Completions.

            :param params:
            :type params: CompletionParams
            :rtype: CompletionList
            """
            filetype = get_filetype(params.text_document.uri)
            if filetype == "":
                return CompletionList(is_incomplete=False, items=[])
            word = self._cursor_word(
                params.text_document.uri,
                params.position,
                False,
                r"[-0-9_a-z]+",
            )
            token = "" if word is None else word[0]
            items = [
                CompletionItem(
                    x,
                    kind=getattr(CompletionItemKind, self.document[x][0]),
                    documentation=self.document[x][1],
                    insert_text=x,
                )
                for x in self.document
                if x.startswith(token) and self.document[x][2] == filetype
            ]
            items += [
                CompletionItem(
                    x,
                    kind=CompletionItemKind.Module,
                    documentation=MarkupContent(
                        kind=MarkupKind.Markdown, value=self.packages[x]
                    ),
                    insert_text=x,
                )
                for x in self.packages
                if x.startswith(token)
            ]
            return CompletionList(False, items)

    def _cursor_line(self, uri: str, position: Position) -> str:
        r"""Cursor line.

        :param uri:
        :type uri: str
        :param position:
        :type position: Position
        :rtype: str
        """
        document = self.workspace.get_document(uri)
        return document.source.splitlines()[position.line]

    def _cursor_word(
        self,
        uri: str,
        position: Position,
        include_all: bool = True,
        regex: str = r"\w+",
    ) -> tuple[str, Range]:
        """Cursor word.

        :param self:
        :param uri:
        :type uri: str
        :param position:
        :type position: Position
        :param include_all:
        :type include_all: bool
        :param regex:
        :type regex: str
        :rtype: tuple[str, Range]
        """
        line = self._cursor_line(uri, position)
        for m in re.finditer(regex, line):
            if m.start() <= position.character <= m.end():
                end = m.end() if include_all else position.character
                return (
                    line[m.start() : end],
                    Range(
                        Position(position.line, m.start()),
                        Position(position.line, end),
                    ),
                )
        return (
            "",
            Range(Position(position.line, 0), Position(position.line, 0)),
        )
