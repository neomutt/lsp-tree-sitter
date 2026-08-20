r"""Misc
========
"""

from gzip import decompress
from pathlib import Path
from subprocess import check_output
from typing import TYPE_CHECKING, Literal
from urllib import request

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pygls.uris import uri_scheme

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def get_data_paths(appname: str) -> list[Path]:
    r"""Get data paths.

    :param appname:
    :type appname: str
    :rtype: list[Path]
    """
    from platformdirs import site_data_dir, user_data_dir

    return [
        Path(d)
        for d in site_data_dir(appname, multipath=True).split(":")
        + [user_data_dir(appname)]
    ]


def get_man(filename: str) -> str:
    r"""Get man.

    :param filename: such as ``make``
    :type filename: str
    :rtype: str
    """
    number = 5
    if filename.find(".") == -1:
        filename += f".{number}"
    else:
        number = int(filename.split(".")[-1])
    filename += "*"
    text = b""
    file = ""
    for path in get_data_paths("man"):
        for file in (path / f"man{number}").glob(filename):
            try:
                with open(file, "rb") as f:
                    text = f.read()
                break
            except Exception:
                continue
    if text == b"":
        raise FileNotFoundError
    _, _, ext = str(file).rpartition(".")
    if ext != str(number):
        text = decompress(text)
    return text.decode()


def get_info(filename: str) -> str:
    r"""Get info.

    :param filename: such as ``automake.info-1``
    :type filename: str
    :rtype: str
    """
    filename += "*"
    text = b""
    file = ""
    for path in get_data_paths("info"):
        for file in path.glob(filename):
            try:
                with open(file, "rb") as f:
                    text = f.read()
                break
            except Exception:
                continue
    if text == b"":
        raise FileNotFoundError
    _, _, ext = str(file).rpartition(".")
    if not ext.startswith("info"):
        text = decompress(text)
    return text.decode()


def get_soup(
    uri: str,
    converter: Literal["pandoc", "groff"] = "pandoc",
    filetype: str = "man",
) -> "BeautifulSoup":
    r"""Get soup.

    pandoc doesn't support mdoc.
    `<https://github.com/jgm/pandoc/issues/9056>`_

    :param uri:
    :type uri: str
    :param converter:
    :type converter: Literal["pandoc", "groff"]
    :param filetype:
    :type filetype: str
    :rtype: BeautifulSoup
    """
    from bs4 import BeautifulSoup, FeatureNotFound

    if uri_scheme(uri):
        with request.urlopen(uri) as f:
            html = f.read()
    else:
        text = get_man(uri)
        if converter == "pandoc":
            from pypandoc import convert_text

            html = convert_text(text, "html", filetype)
        else:
            html = check_output(
                ["groff", "-m", filetype, "-Thtml"],
                input=text.encode(),
            ).decode()
    try:
        soup = BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(html, "html.parser")
    return soup


def get_md_tokens(filename: str) -> list[Token]:
    r"""Get markdown tokens.

    :param filename:
    :type filename: str
    :rtype: list[Token]
    """
    from pypandoc import convert_text

    md = MarkdownIt("commonmark", {})
    text = get_man(filename)
    return md.parse(convert_text(text, "markdown", "man"))
