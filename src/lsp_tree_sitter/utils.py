r"""Utils
=========

Some common functions used by formatters and linters.
"""

import os
import sys
from collections.abc import Callable
from typing import Any, Literal

from . import Finder


def get_paths(
    paths: list[str], get_filetype: Callable[[str], str]
) -> dict[str, list[str]]:
    r"""Get paths.

    :param paths:
    :type paths: list[str]
    :param get_filetype: return ``Literal["ft1", "ft2", ...] | Literal[""]``
    :type get_filetype: Callable[[str], str]
    :rtype: dict[str, list[str]]
    """
    filetype_paths = {
        k: []
        for k in get_filetype.__annotations__["return"].__args__[0].__args__
        if k != ""
    }
    for path in paths:
        filetype = get_filetype(path)
        for _filetype, filepaths in filetype_paths.items():
            if filetype == _filetype:
                filepaths += [path]
    return filetype_paths


def get_finders(
    classes: list[type[Finder]] | None = None,
) -> tuple[list[Finder], list[type[Finder]]]:
    r"""Get finders.

    :param classes:
    :type classes: list[type[Finder]] | None
    :rtype: tuple[list[Finder], list[type[Finder]]]
    """
    if classes is None:
        from .finders import ErrorFinder

        classes = [ErrorFinder]

    finders = []
    finder_classes = []
    for cls in classes:
        if cls.__init__.__annotations__.get("filetype"):
            finder_classes += [cls]
        else:
            finders += [cls()]
    return finders, finder_classes


def pygmentize(text: str, filetype: str) -> None:
    r"""Pygmentize.

    :param text:
    :type text: str
    :param filetype:
    :type filetype: str
    :rtype: None
    """
    TERM = os.getenv("TERM", "xterm")
    if not sys.stdout.isatty():
        TERM = "dumb"
    try:
        from pygments import highlight
        from pygments.formatters import get_formatter_by_name
        from pygments.lexers import get_lexer_by_name

        if TERM.split("-")[-1] == "256color":
            formatter_name = "terminal256"
        elif TERM != "dumb":
            formatter_name = "terminal"
        else:
            formatter_name = None
        if formatter_name:
            formatter = get_formatter_by_name(formatter_name)
            lexer = get_lexer_by_name(filetype)
            print(highlight(text, lexer, formatter), end="")
    except ImportError:
        TERM = "dumb"
    if TERM == "dumb":
        print(text)


def pprint(
    obj: object,
    filetype: Literal["json", "yaml", "toml"] = "json",
    *args: Any,
    **kwargs: Any,
) -> None:
    r"""Pprint.

    :param obj:
    :type obj: object
    :param filetype:
    :type filetype: Literal["json", "yaml", "toml"]
    :param args:
    :type args: Any
    :param kwargs:
    :type kwargs: Any
    :rtype: None
    """
    if filetype == "json":
        from json import dumps
    elif filetype == "yaml":
        from yaml import dump as dumps
    elif filetype == "toml":
        from tomli_w import dumps

    text = dumps(obj, *args, **kwargs)
    pygmentize(text, filetype)
