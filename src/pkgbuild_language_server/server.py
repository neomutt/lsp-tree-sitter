r"""Server
==========
"""
import re
from typing import Any, Tuple

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

from .documents import check_extension, get_document, get_packages
from .utils import diagnostic


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

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: TextDocumentPositionParams) -> Hover | None:
            r"""Hover.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: Hover | None
            """
            if not check_extension(params.text_document.uri):
                return None
            if check_extension(params.text_document.uri) == "PKGBUILD":
                # PKGBUILD contains package_XXX
                pat = r"[a-z]+"
            else:
                # *.install contains pre_install()
                pat = r"[a-z_]+"
            word = self._cursor_word(
                params.text_document.uri, params.position, True, pat
            )
            if not word:
                return self.hover(params)
            result = self.document.get(word[0])
            if not result:
                return self.hover(params)
            doc = f"**{result[0]}**\n{result[1]}"
            return Hover(
                contents=MarkupContent(kind=MarkupKind.Markdown, value=doc),
                range=word[1],
            )

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            r"""Completions.

            :param params:
            :type params: CompletionParams
            :rtype: CompletionList
            """
            if not check_extension(params.text_document.uri):
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
                    label=x,
                    kind=getattr(CompletionItemKind, self.document[x][0]),
                    documentation=self.document[x][1],
                    insert_text=x,
                )
                for x in self.document
                if x.startswith(token)
                and self.document[x][2]
                == check_extension(params.text_document.uri)
            ]
            items += [
                CompletionItem(
                    label=x,
                    kind=CompletionItemKind.Module,
                    documentation=MarkupContent(
                        kind=MarkupKind.Markdown, value=self.packages[x]
                    ),
                    insert_text=x,
                )
                for x in self.packages
                if x.startswith(token)
            ]
            return CompletionList(is_incomplete=False, items=items)

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams) -> None:
            r"""Did change.

            :param params:
            :type params: DidChangeTextDocumentParams
            :rtype: None
            """
            if not check_extension(params.text_document.uri):
                return None
            doc = self.workspace.get_document(params.text_document.uri)
            source = doc.source
            if doc.path is None:
                return None
            diagnostics = [
                Diagnostic(
                    range=Range(
                        Position(0, 0),
                        Position(0, len(source.splitlines()[0])),
                    ),
                    message=msg,
                    severity=getattr(DiagnosticSeverity, severity),
                    source="namcap",
                )
                for msg, severity in diagnostic(doc.path)
            ]
            self.publish_diagnostics(doc.uri, diagnostics)

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

    def hover(self, params: TextDocumentPositionParams) -> Hover | None:
        r"""Hover.

        :param params:
        :type params: TextDocumentPositionParams
        :rtype: Hover | None
        """
        word = self._cursor_word(
            params.text_document.uri, params.position, True, r"[-0-9_a-z]+"
        )
        if not word:
            return None
        doc = self.packages.get(word[0])
        if not doc:
            return None
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=doc),
            range=word[1],
        )
