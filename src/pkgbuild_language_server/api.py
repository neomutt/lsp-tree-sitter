r"""Api
=======
"""
import os
from gzip import decompress

from markdown_it import MarkdownIt
from markdown_it.token import Token
from platformdirs import site_data_dir
from pypandoc import convert_text


def get_content(tokens: list[Token]) -> str:
    r"""Get content.

    :param tokens:
    :type tokens: list[Token]
    :rtype: str
    """
    return "\n".join(
        [token.content.replace("\n", " ") for token in tokens if token.content]
    )


def init_document() -> dict[str, tuple[str, str]]:
    r"""Init document.

    :rtype: dict[str, tuple[str, str]]
    """
    md = MarkdownIt("commonmark", {})
    with open(
        os.path.join(
            os.path.join(site_data_dir("man"), "man5"), "PKGBUILD.5.gz"
        ),
        "rb",
    ) as f:
        tokens = md.parse(
            convert_text(decompress(f.read()).decode(), "markdown", "man")
        )
    # **pkgname (array)**
    #
    # > Either the name of the package or an array of names for split
    # > packages. Valid characters for members of this array are
    # > alphanumerics, and any of the following characters: "@ . \_ + -".
    # > Additionally, names are not allowed to start with hyphens or dots.
    indices = [
        index
        for index, token in enumerate(tokens)
        if token.content.startswith("**")
        and token.content.endswith("**")
        and token.level == 1
    ]
    blockquote_close_indices = [
        index
        for index, token in enumerate(tokens)
        if token.type == "blockquote_close"
    ]
    close_indices = [
        min(
            [
                blockquote_close_index
                for blockquote_close_index in blockquote_close_indices
                if blockquote_close_index > index
            ]
        )
        for index in indices
    ]
    items = {}
    for index, close_index in zip(indices, close_indices):
        children = tokens[index].children
        if children is None:
            continue
        vars = children[2].content.split()
        kind = vars[1].lstrip("(").rstrip(")") if len(vars) > 1 else ""
        kind = {"": "Variable", "array": "Field"}.get(kind, kind)
        items[vars[0]] = (
            kind,
            get_content(tokens[index + 1 : close_index]),
        )
    return items
