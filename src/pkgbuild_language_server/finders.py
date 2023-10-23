r"""Finders
===========
"""
from contextlib import suppress
from copy import deepcopy

from lsprotocol.types import Diagnostic, DiagnosticSeverity

from .tree_sitter_lsp import UNI, Finder


class PackageFinder(Finder):
    r"""Packagefinder."""

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        parent = uni.node.parent
        if parent is None:
            return False
        if parent.parent is None:
            return False
        return (
            uni.node.type == "word"
            and parent.type == "array"
            and parent.parent.type == "variable_assignment"
            and UNI.node2text(parent.parent.children[0])
            in [
                "depends",
                "optdepends",
                "makedepends",
                "conflicts",
                "provides",
            ]
        )


class InvalidKeywordFinder(Finder):
    r"""Invalidkeywordfinder."""

    def __init__(
        self,
        keywords: dict[str, str],
        filetype: str,
        message: str = "{{uni.get_text()}}: should be {{type}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param keywords:
        :type keywords: dict[str, str]
        :param filetype:
        :type filetype: str
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.keywords = deepcopy(keywords)
        # pkgname can be an array or a scalar
        with suppress(KeyError):
            self.keywords.pop("pkgname")
        self.filetype = filetype

    @staticmethod
    def is_correct_declaration(uni: UNI, _type: str) -> bool:
        r"""Is correct declaration.

        :param uni:
        :type uni: UNI
        :param _type:
        :type _type: str
        :rtype: bool
        """
        parent = uni.node.parent
        if parent is None:
            return False
        return (
            _type == "Variable"
            and uni.node.type == "variable_name"
            and parent.type == "variable_assignment"
            and parent.children[-1].type != "array"
            or _type == "Field"
            and uni.node.type == "variable_name"
            and parent.type == "variable_assignment"
            and parent.children[-1].type == "array"
            or _type == "Function"
            and uni.node.type == "word"
            and parent.type == "function_definition"
        )

    @staticmethod
    def is_correct(uni: UNI, _type: str) -> bool:
        r"""Is correct.

        :param uni:
        :type uni: UNI
        :param _type:
        :type _type: str
        :rtype: bool
        """
        parent = uni.node.parent
        if parent is None:
            return False
        return (
            InvalidKeywordFinder.is_correct_declaration(uni, _type)
            or _type in {"Variable", "Field"}
            and uni.node.type == "variable_name"
            and parent.type in {"expansion", "simple_expansion"}
            or _type == "Function"
            and uni.node.type == "word"
            and parent.type == "command_name"
        )

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        text = uni.get_text()
        # PKGBUILD contains package_XXX
        if self.filetype == "PKGBUILD":
            text = text.split("_")[0]
        if text not in self.keywords:
            return False
        _type = self.keywords[text]
        return not self.is_correct(uni, _type)

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        r"""Uni2diagnostic.

        :param uni:
        :type uni: UNI
        :rtype: Diagnostic
        """
        text = uni.get_text()
        _type = self.keywords[text]
        return uni.get_diagnostic(self.message, self.severity, type=_type)
