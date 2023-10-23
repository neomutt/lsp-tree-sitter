r"""Finders
===========
"""
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
