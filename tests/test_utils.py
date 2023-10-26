r"""Test utils."""
import os
from typing import Literal

from tree_sitter_lsp.utils import get_paths

FILETYPE = Literal["python", "c"]


def get_filetype(path: str) -> FILETYPE | Literal[""]:
    r"""Get filetype.

    :param path:
    :type path: str
    :rtype: FILETYPE | Literal[""]
    """
    ext = path.split(os.path.extsep)[-1]
    if ext == "c":
        return "c"
    if ext == "py":
        return "python"
    return ""


class Test:
    r"""Test."""

    @staticmethod
    def test_get_paths() -> None:
        r"""Test get paths.

        :rtype: None
        """
        result = get_paths(["a.c", "b.c", "c.py"], get_filetype)
        expected = {"c": ["a.c", "b.c"], "python": ["c.py"]}
        assert result == expected
