r"""Misc
========
"""

from typing import Any

from .. import FILETYPE


def get_schema(filetype: FILETYPE = "{{ language }}") -> dict[str, Any]:
    r"""Get schema.

    :param filetype:
    :type filetype: FILETYPE
    :rtype: dict[str, Any]
    """
    from .{{ language }} import init_schema

    return init_schema()[filetype]
