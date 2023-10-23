r"""Utils
=========
"""
from typing import Callable, Literal

from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from tree_sitter import Tree

from .documents import get_document, get_filetype
from .finders import InvalidKeywordFinder
from .tree_sitter_lsp.diagnose import check as _check
from .tree_sitter_lsp.finders import ErrorFinder, MissingFinder

DIAGNOSTICS_FINDERS = [
    ErrorFinder(),
    MissingFinder(),
]


def get_paths(paths: list[str]) -> dict[str, list[str]]:
    r"""Get paths.

    :param paths:
    :type paths: list[str]
    :rtype: dict[str, list[str]]
    """
    _paths = {"PKGBUILD": [], "install": []}
    for path in paths:
        filetype = get_filetype(path)
        for _filetype, filepaths in _paths.items():
            if filetype == _filetype:
                filepaths += [path]
    return _paths


def get_keywords(
    document: dict[str, tuple[str, str, str]]
) -> dict[str, dict[str, str]]:
    r"""Get keywords.

    :param document:
    :type document: dict[str, tuple[str, str, str]]
    :rtype: dict[str, dict[str, str]]
    """
    keywords = {"PKGBUILD": {}, "install": {}}
    for k, v in document.items():
        for filetype, words in keywords.items():
            if v[2] == filetype:
                words[k] = v[0]
    return keywords


def check(
    paths: list[str],
    parse: Callable[[bytes], Tree],
    color: Literal["auto", "always", "never"] = "auto",
) -> int:
    r"""Check.

    :param paths:
    :type paths: list[str]
    :param parse:
    :type parse: Callable[[bytes], Tree]
    :param color:
    :type color: Literal["auto", "always", "never"]
    :rtype: int
    """
    document = get_document()
    keywords = get_keywords(document)
    _paths = get_paths(paths)
    return sum(
        _check(
            _paths[filetype],
            DIAGNOSTICS_FINDERS
            + [
                InvalidKeywordFinder(keywords[filetype], filetype),
            ],
            parse,
            color,
        )
        for filetype in ["PKGBUILD", "install"]
    )


def namcap(path: str, source: str) -> list[Diagnostic]:
    r"""Namcap.

    :param path:
    :type path: str
    :param source:
    :type source: str
    :rtype: list[Diagnostic]
    """
    try:
        from Namcap.rules import all_rules
    except ImportError:
        return []
    from Namcap.package import load_from_pkgbuild
    from Namcap.ruleclass import PkgbuildRule
    from Namcap.tags import format_message

    pkginfo = load_from_pkgbuild(path)
    items = {}
    for value in all_rules.values():
        rule = value()
        if isinstance(rule, PkgbuildRule):
            rule.analyze(pkginfo, "PKGBUILD")  # type: ignore
        for msg in rule.errors:
            items[format_message(msg)] = DiagnosticSeverity.Error
        for msg in rule.warnings:
            items[format_message(msg)] = DiagnosticSeverity.Warning
    end = len(source.splitlines()[0])
    return [
        Diagnostic(Range(Position(0, 0), Position(0, end)), msg, severity)
        for msg, severity in items.items()
    ]
