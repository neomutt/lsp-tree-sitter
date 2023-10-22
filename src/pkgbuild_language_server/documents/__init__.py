r"""Documents
=============
"""
import json
import os
from typing import Literal

from platformdirs import user_cache_dir

from .. import CACHE


def get_filetype(uri: str) -> Literal["install", "PKGBUILD", ""]:
    r"""Get filetype.

    :param uri:
    :type uri: str
    :rtype: Literal["install", "PKGBUILD", ""]
    """
    if uri.split(os.path.extsep)[-1] == "install":
        return "install"
    if os.path.basename(uri) == "PKGBUILD":
        return "PKGBUILD"
    return ""


def get_document(
    method: Literal["builtin", "cache", "system"] = "builtin"
) -> dict[str, tuple[str, str, str]]:
    r"""Get document. ``builtin`` will use builtin pkgbuild.json. ``cache``
    will generate a cache from ``${XDG_CACHE_DIRS:-/usr/share}
    /man/man5/PKGBUILD.5.gz``. ``system`` is same as ``cache`` except it
    doesn't generate cache. We use ``builtin`` as default.

    :param method:
    :type method: Literal["builtin", "cache", "system"]
    :rtype: dict[str, tuple[str, str, str]]
    """
    if method == "builtin":
        file = os.path.join(
            os.path.join(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), "assets"
                ),
                "json",
            ),
            "pkgbuild.json",
        )
        with open(file, "r") as f:
            document = json.load(f)
    elif method == "cache":
        from .builtin import init_document

        if not os.path.exists(user_cache_dir("pkgbuild.json")):
            document = init_document()
            with open(user_cache_dir("pkgbuild.json"), "w") as f:
                json.dump(document, f)
        else:
            with open(user_cache_dir("pkgbuild.json"), "r") as f:
                document = json.load(f)
    else:
        from .builtin import init_document

        document = init_document()
    return document


def get_packages() -> dict[str, str]:
    r"""Get packages.

    :rtype: dict[str, str]
    """
    try:
        with open(CACHE, "r") as f:
            packages = json.load(f)
    except FileNotFoundError:
        packages = {}
    return packages
