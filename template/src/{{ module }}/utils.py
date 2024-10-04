r"""Utils
=========
"""

import json
import os
from typing import Any

from tree_sitter import Language, Parser, Query
from tree_sitter_{{ language }} import language as get_language_ptr

from . import FILETYPE

SCHEMAS = {}
QUERIES = {}
parser = Parser()
parser.language = Language(get_language_ptr())


def get_query(name: str, filetype: FILETYPE = "{{ language }}") -> Query:
    r"""Get query.

    :param name:
    :type name: str
    :param filetype:
    :type filetype: FILETYPE
    :rtype: Query
    """
    if name not in QUERIES:
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "assets",
                "queries",
                f"{name}{os.path.extsep}scm",
            )
        ) as f:
            text = f.read()

        QUERIES[name] = parser.language.query(text)
    return QUERIES[name]


def get_schema(filetype: FILETYPE = "{{ language }}") -> dict[str, Any]:
    r"""Get schema.

    :param filetype:
    :type filetype: FILETYPE
    :rtype: dict[str, Any]
    """
    if filetype not in SCHEMAS:
        file = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "json",
            f"{filetype}.json",
        )
        with open(file) as f:
            SCHEMAS[filetype] = json.load(f)
    return SCHEMAS[filetype]
