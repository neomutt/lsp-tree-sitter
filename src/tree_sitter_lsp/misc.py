r"""Misc
========
"""

from gzip import decompress
from itertools import chain
from subprocess import check_output  # nosec: B404
from typing import Literal
from urllib import request

from bs4 import BeautifulSoup, FeatureNotFound
from markdown_it import MarkdownIt
from markdown_it.token import Token
from platformdirs import site_data_path, user_data_path
from pygls.uris import uri_scheme
from pypandoc import convert_text


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
    path = ""
    for path in chain(
        (user_data_path("man") / f"man{number}").glob(filename),
        (site_data_path("man") / f"man{number}").glob(filename),
    ):
        try:
            with open(path, "rb") as f:
                text = f.read()
            break
        except Exception:  # nosec: B112
            continue
    if text == b"":
        raise FileNotFoundError
    _, _, ext = str(path).rpartition(".")
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
    path = ""
    for path in chain(
        user_data_path("info").glob(filename),
        site_data_path("info").glob(filename),
    ):
        try:
            with open(path, "rb") as f:
                text = f.read()
            break
        except Exception:  # nosec: B112
            continue
    if text == b"":
        raise FileNotFoundError
    _, _, ext = str(path).rpartition(".")
    if not ext.startswith("info"):
        text = decompress(text)
    return text.decode()


def html2soup(html: str) -> BeautifulSoup:
    r"""Html2soup.

    :param html:
    :type html: str
    :rtype: BeautifulSoup
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(html, "html.parser")
    return soup


def get_soup(
    uri: str,
    converter: Literal["pandoc", "groff"] = "pandoc",
    filetype: str = "man",
) -> BeautifulSoup:
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
    if uri_scheme(uri):
        with request.urlopen(uri) as f:  # nosec: B310
            html = f.read()
    else:
        text = get_man(uri)
        if converter == "pandoc":
            html = convert_text(text, "html", filetype)
        else:
            html = check_output(  # nosec: B603 B607
                ["groff", "-m", filetype, "-Thtml"],
                input=text.encode(),
            ).decode()
    return html2soup(html)


def get_md_tokens(filename: str) -> list[Token]:
    r"""Get markdown tokens.

    :param filename:
    :type filename: str
    :rtype: list[Token]
    """
    md = MarkdownIt("commonmark", {})
    text = get_man(filename)
    return md.parse(convert_text(text, "markdown", "man"))
