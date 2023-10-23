r"""Server
==========
"""
from typing import Any

from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_LINK,
    TEXT_DOCUMENT_HOVER,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    DidChangeTextDocumentParams,
    DocumentLink,
    DocumentLinkParams,
    Hover,
    InitializeParams,
    MarkupContent,
    MarkupKind,
    Position,
    TextDocumentPositionParams,
)
from pygls.server import LanguageServer

from .documents import get_document, get_filetype, get_packages
from .finders import PackageFinder
from .parser import parse
from .tree_sitter_lsp.diagnose import get_diagnostics
from .tree_sitter_lsp.finders import PositionFinder
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

        @self.feature(TEXT_DOCUMENT_DOCUMENT_LINK)
        def document_link(params: DocumentLinkParams) -> list[DocumentLink]:
            r"""Get document links.

            :param params:
            :type params: DocumentLinkParams
            :rtype: list[DocumentLink]
            """
            filetype = get_filetype(params.text_document.uri)
            if filetype == "":
                return []
            document = self.workspace.get_document(params.text_document.uri)
            return PackageFinder().get_document_links(
                document.uri,
                self.trees[document.uri],
                "https://archlinux.org/packages/{{uni.get_text()}}",
            )

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
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(
                Position(params.position.line, params.position.character - 1)
            ).find(document.uri, self.trees[document.uri])
            if uni is None:
                return CompletionList(False, [])
            text = uni.get_text()
            parent = uni.node.parent
            if parent is None:
                return CompletionList(False, [])
            if parent.type == "array":
                return CompletionList(
                    False,
                    [
                        CompletionItem(
                            k,
                            kind=CompletionItemKind.Module,
                            documentation=MarkupContent(
                                MarkupKind.Markdown, v
                            ),
                            insert_text=k,
                        )
                        for k, v in self.packages.items()
                        if k.startswith(text)
                    ],
                )
            return CompletionList(
                False,
                [
                    CompletionItem(
                        k,
                        kind=getattr(CompletionItemKind, v[0]),
                        documentation=v[1],
                        insert_text=k,
                    )
                    for k, v in self.document.items()
                    if k.startswith(text) and v[2] == filetype
                ],
            )
