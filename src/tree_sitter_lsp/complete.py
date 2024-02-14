r"""Complete
============
"""

import os
from glob import glob
from pathlib import Path
from typing import Any

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    MarkupContent,
    MarkupKind,
)

from . import UNI


def get_completion_list_by_enum(
    text: str, property: dict[str, Any]
) -> CompletionList:
    r"""Get completion list by enum. ``property.items`` must contains
    ``enum``, ``oneOf.enum``, ``anyOf.enum`` or ``allOf``.

    :param text:
    :type text: str
    :param property:
    :type property: dict[str, Any]
    :rtype: CompletionList
    """
    # if contains .items, it is an array
    property = property.get("items", property)
    enum = property.get(
        "enum",
        property.get(
            "oneOf", property.get("anyOf", property.get("allOf", [{}]))
        )[0].get("enum", []),
    )
    items = []
    for k in enum:
        if k is None:
            continue
        if not isinstance(k, str):
            k = str(k)
        if k.startswith(text):
            items += [
                CompletionItem(
                    k,
                    kind=CompletionItemKind.Constant,
                    insert_text=k,
                )
            ]
    return CompletionList(False, items)


def get_completion_list_by_uri(
    text: str, uri: str, exprs: dict[str, str] | None = None
) -> CompletionList:
    r"""Get completion list by ``uri``. Don't need to filter by ``text``
    because all results are started with ``text``.

    :param text:
    :type text: str
    :param uri:
    :type uri: str
    :param exprs:
    :type exprs: dict[str, str] | None
    :rtype: CompletionList
    """
    if exprs is None:
        exprs = {"*": "text", "**/*": "text"}
    dirname = os.path.dirname(UNI.uri2path(uri))
    prefix = os.path.join(dirname, text)
    items = []
    for expr, filetype in exprs.items():
        for file in glob(os.path.join(dirname, expr), recursive=True):
            if not file.startswith(prefix):
                continue
            if os.path.isdir(file):
                file += os.path.sep
            items += [
                CompletionItem(
                    file.rpartition(dirname + os.path.sep)[-1],
                    kind=CompletionItemKind.File
                    if os.path.isfile(file)
                    else CompletionItemKind.Folder,
                    documentation=MarkupContent(
                        MarkupKind.Markdown,
                        f"""```{filetype}
{Path(file).read_text()}
```""",
                    )
                    if os.path.isfile(file)
                    else "\n".join(os.listdir(file)),
                    insert_text=file.rpartition(dirname + os.path.sep)[-1],
                )
            ]
    return CompletionList(False, items)
