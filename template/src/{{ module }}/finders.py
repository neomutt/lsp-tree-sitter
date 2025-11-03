r"""Finders
===========
"""

from dataclasses import dataclass

from lsp_tree_sitter.finders import ErrorFinder, QueryFinder, SchemaFinder
from lsprotocol.types import DiagnosticSeverity

from .schema import {{ language | title }}Trie
from .utils import get_query, get_schema


@dataclass(init=False)
class Import{{ language | title }}Finder(QueryFinder):
    r"""Import{{ language | title }}Finder."""

    def __init__(
        self,
        message: str = "\{\{uni.text\}\}: error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ):
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        """
        super().__init__(get_query("import"), message, severity)


@dataclass(init=False)
class {{ language | title }}Finder(SchemaFinder):
    r"""{{ language | title }}finder."""

    def __init__(self) -> None:
        r"""Init.

        :rtype: None
        """
        super().__init__(get_schema(), {{ language | title }}Trie)


DIAGNOSTICS_FINDER_CLASSES = [
    ErrorFinder,
    {{ language | title }}Finder,
]
FORMAT_FINDER_CLASSES = []
